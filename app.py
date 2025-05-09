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
        if given_oz == true_oz:     # exact match
            feedback[ing] = f"{given_oz} oz is Correct!"
            correct += 2                       # +2 points: right ing & amount
        elif given_oz > 0:
            feedback[ing] = f"{given_oz} oz is Incorrect (need {true_oz} oz)"
            correct += 1                       # +1 point: ingredient present
        else:
            feedback[ing] = f"missing – need {true_oz} oz)"
        
    return correct, feedback
# ----- routes --------------------------------------------------------------
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/learn/<int:page_id>")
def learn_page(page_id):
    with open("./learning_data.json") as f:
        lessons = json.load(f)
    if page_id > len(lessons):
        return redirect(url_for("quiz"))  # change as needed
    lesson = lessons[page_id - 1]
    return render_template("learn.html", lesson=lesson, page_id=page_id, total=len(lessons))


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
    data = request.get_json(force=True)      # parse the JSON body
    ingredients = data.get('ingredients', {})  # {name: amount, …}
            # stash in cookie-backed session
    drink = session.get("drink")
    if drink is None:
        return jsonify({"error": "no drink in session"}), 400
    if str(ingredients) != "{}":
        score, feedback = grade(drink, ingredients)
        session['attempt'] = feedback
        session['cur_score'] = score
    return jsonify({'redirect': url_for('score')})
    

@app.route("/score")
def score():
    drink = session.get("drink")
    best_score = DRINKS[drink]["best"]
    attempt = session.pop('attempt', 0)   # pull once, then forget
    cur_score = session.pop('cur_score', 0)
    if best_score < cur_score:
        DRINKS[drink]["best"] = cur_score
        best_score = cur_score
    if attempt is None:                      # user refreshed directly
        return redirect(url_for('quiz'))    # or some landing page
    # pass “attempt” into the template for display / grading
    return render_template('score.html', attempt=attempt, drink=drink, best_score=best_score, cur_score=cur_score)

# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)