from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json, os

app = Flask(__name__)
app.secret_key = "CHANGE-ME"          # session signing

# ----- load drink data once -----------------------------------------------
with open("drinks.json", "r") as f:
    DRINKS = json.load(f)

# helper --------------------------------------------------------------------
def grade(drink_name, attempt):
    """return (score, feedback_dict) comparing attempt vs true recipe"""
    recipe = DRINKS[drink_name]["recipe"]
    correct   = 0
    feedback  = {}
    for ing, true_oz in recipe.items():
        given_oz = attempt.get(ing, 0)
        if abs(given_oz - true_oz) < 0.01:     # exact match
            feedback[ing] = f"✓  {given_oz} oz (perfect)"
            correct += 2                       # +2 points: right ing & amount
        elif given_oz > 0:
            feedback[ing] = f"½  {given_oz} oz (wrong amount – need {true_oz})"
            correct += 1                       # +1 point: ingredient present
        else:
            feedback[ing] = f"✗  (missing – need {true_oz} oz)"
    return correct, feedback


# ----- routes --------------------------------------------------------------
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/learn")
def learn():
    return render_template("learn.html")

@app.route("/quiz")
def quiz():
    return render_template("quiz.html", drinks=DRINKS)

@app.route("/make/<drink>")
def make_drink(drink):
    if drink not in DRINKS:
        return redirect(url_for("quiz"))
    session["drink"] = drink
    return render_template("make_drink.html",
                           drink_name=drink,
                           recipe=DRINKS[drink]["recipe"],
                           best=DRINKS[drink].get("best", 0))

@app.route("/serve", methods=["POST"])
def serve():
    payload = request.get_json(force=True)
    attempt = {k: float(v) for k, v in payload.get("ingredients", {}).items()}
    drink   = session.get("drink")
    if drink is None:
        return jsonify({"error": "no drink in session"}), 400

    score, feedback = grade(drink, attempt)

    # update best score in memory – in production write to DB
    DRINKS[drink]["best"] = max(score, DRINKS[drink].get("best", 0))

    session["last_score"] = score
    session["feedback"]   = feedback
    return jsonify({"redirect": url_for("score")})

@app.route("/score")
def score():
    score    = session.pop("last_score", None)
    feedback = session.pop("feedback", {})
    drink    = session.pop("drink", None)
    if score is None:
        return redirect(url_for("quiz"))
    best     = DRINKS[drink]["best"]
    return render_template("score.html",
                           score=score,
                           best=best,
                           feedback=feedback,
                           drink=drink)

# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
