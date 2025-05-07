// very small helper for our one page
$(function () {
    let selectedIngredient = null;
    let working = {};           // { "Tequila": 1.5, ... }
    
    const ingredients = document.querySelectorAll('.ingredient');
    const addBtn = document.querySelector('#add-btn');

    // Add click event to highlight ingredients
    ingredients.forEach(ingredient => {
        ingredient.addEventListener('click', () => {
        // Remove highlight from previously selected ingredient
        if (selectedIngredient) {
            selectedIngredient.classList.remove('highlight');
        }
        // Highlight the clicked ingredient
        ingredient.classList.add('highlight');
        selectedIngredient = ingredient;
        });
    });

  // Clear highlight when "Enter" button is clicked
  addBtn.addEventListener('click', () => {
    if (selectedIngredient) {
      selectedIngredient.classList.remove('highlight');
      selectedIngredient = null;
    }
  });
    // ----- drag & drop ------------------------------------------------------
    $(".ingredient").on("dragstart", function (e) {
        selectedIngredient = $(this).data("ingredient");
        $("#oz-input").focus();
    });
  
    $("#glass").on("dragover", e => e.preventDefault());   // allow drop
    $("#glass").on("drop",     e => e.preventDefault());   // we only care about click→enter
  
    // ----- add ounces -------------------------------------------------------
    $("#add-btn").on("click", () => {
        const oz = parseFloat($("#oz-input").val());
        if (!selectedIngredient || isNaN(oz) || oz <= 0) return;
  
        working[selectedIngredient] = (working[selectedIngredient] || 0) + oz;
        $("#current-list").html(Object.entries(working)
          .map(([k,v]) => `${k}: ${v.toFixed(2)} oz`).join("<br>"));
        $("#oz-input").val("");
        selectedIngredient = null;
    });
  
    // ----- trash / reset ----------------------------------------------------
    $("#trash-btn").on("click", () => {
        working = {};
        $("#current-list").empty();
    });
  
    // ----- serve cocktail ---------------------------------------------------
    $("#serve-btn").on("click", () => {
        fetch("/serve", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ ingredients: working })
        })
        .then(r => r.json())
        .then(data => { window.location = data.redirect; })
        .catch(console.error);
    });
  });
  