const state = {
    mood: null,
    hunger: null,
    diet: null,
    food_type: null,
};


document.addEventListener("DOMContentLoaded", () => {

    setupOptionButtons();

    setupFindFood();

    setupStartOver();

});


/* ============================================================
   OPTION BUTTONS
   ============================================================ */

function setupOptionButtons() {

    const buttons = document.querySelectorAll(
        ".option-button"
    );

    buttons.forEach(button => {

        button.addEventListener(
            "click",
            () => {

                const group = button.dataset.group;
                const value = button.dataset.value;


                // Remove selection from same group

                document
                    .querySelectorAll(
                        `.option-button[data-group="${group}"]`
                    )
                    .forEach(item => {

                        item.classList.remove(
                            "selected"
                        );

                    });


                // Select current

                button.classList.add(
                    "selected"
                );


                // Save state

                state[group] = value;

            }
        );

    });

}


/* ============================================================
   FIND FOOD
   ============================================================ */

function setupFindFood() {

    const button = document.getElementById(
        "findFoodButton"
    );

    if (!button) {
        return;
    }

    button.addEventListener(
        "click",
        getRecommendations
    );

}


/* ============================================================
   API REQUEST
   ============================================================ */

async function getRecommendations() {

    const message = document.getElementById(
        "formMessage"
    );

    const resultsSection = document.getElementById(
        "resultsSection"
    );

    const resultsGrid = document.getElementById(
        "resultsGrid"
    );

    const budgetInput = document.getElementById(
        "budgetInput"
    );


    if (!message ||
        !resultsSection ||
        !resultsGrid ||
        !budgetInput) {

        return;

    }


    const budget = budgetInput.value;


    // --------------------------------------------
    // Validation
    // --------------------------------------------

    if (!state.mood) {

        message.textContent =
            "Please select your mood.";

        return;

    }


    if (!state.hunger) {

        message.textContent =
            "Please select your hunger level.";

        return;

    }


    if (!state.diet) {

        message.textContent =
            "Please select your dietary preference.";

        return;

    }


    if (!state.food_type) {

        message.textContent =
            "Please select the type of food.";

        return;

    }


    if (!budget || Number(budget) <= 0) {

        message.textContent =
            "Please enter a valid budget.";

        return;

    }


    message.textContent = "";


    // --------------------------------------------
    // Loading
    // --------------------------------------------

    resultsSection.classList.remove(
        "hidden"
    );


    resultsGrid.innerHTML = `
        <div class="loading">
            Finding food that matches you...
        </div>
    `;


    resultsSection.scrollIntoView({
        behavior: "smooth",
        block: "start",
    });


    // --------------------------------------------
    // Build API URL
    // --------------------------------------------

    const params = new URLSearchParams({

        mood: state.mood,

        hunger: state.hunger,

        budget: budget,

        diet: state.diet,

        food_type: state.food_type,

        limit: 10,

    });


    try {

        const response = await fetch(
            `/api/recommendations/?${params.toString()}`
        );


        const data =
            await response.json();


        if (!response.ok) {

            throw new Error(
                "Recommendation request failed."
            );

        }


        if (!data.success) {

            throw new Error(
                "Could not get recommendations."
            );

        }


        renderResults(
            data.results
        );


    } catch (error) {

        console.error(error);


        resultsGrid.innerHTML = `
            <div class="loading">
                Something went wrong while finding
                your food. Please try again.
            </div>
        `;

    }

}


/* ============================================================
   RENDER RESULTS
   ============================================================ */

function renderResults(results) {

    const grid = document.getElementById(
        "resultsGrid"
    );


    if (!grid) {
        return;
    }


    if (!results.length) {

        grid.innerHTML = `
            <div class="loading">

                We couldn't find matching foods.

                Try increasing your budget or
                changing your preferences.

            </div>
        `;

        return;

    }


    grid.innerHTML = results
        .map(createFoodCard)
        .join("");

    results.forEach(
    result => {

        if (result.food_id) {

            loadRecommendationFeedback(
                result.food_id
            );

        }

    }
);

}


/* ============================================================
   FOOD CARD
   ============================================================ */

function createFoodCard(result) {

    const image = result.image_url
        ? result.image_url
        : "https://placehold.co/800x600?text=MoodBite";


    const score = Number(
        result.score || 0
    ).toFixed(1);


    const price =
        result.price &&
        result.price.avg_inr != null

            ? `₹${Math.round(
                result.price.avg_inr
            )}`

            : "Price unavailable";


    const calories =
        result.nutrition &&
        result.nutrition.calories != null

            ? `${Math.round(
                result.nutrition.calories
            )} kcal`

            : "Calories N/A";


    const protein =
        result.nutrition &&
        result.nutrition.protein_g != null

            ? `${Number(
                result.nutrition.protein_g
            ).toFixed(1)}g protein`

            : "Protein N/A";

    const reasons = (
        result.reasons || []
    )
        .slice(0, 4)
        .map(
            reason => `
                <div class="match-reason">
                    <span class="match-reason-icon">✓</span>
                    <span>${escapeHtml(reason)}</span>
                </div>
            `
        )
        .join("");

    return `
        <article
            class="food-card"
            onclick="openFoodDetail('${escapeAttribute(
                result.food_id
            )}')"
            role="button"
            tabindex="0"
        >

            <img
                class="food-image"
                src="${escapeAttribute(image)}"
                alt="${escapeAttribute(result.name)}"
                loading="lazy"

                onerror="
                    this.src='https://placehold.co/800x600?text=MoodBite'
                "
            >

            <div class="food-card-content">

                <div class="food-card-top">

                    <h3>
                        ${escapeHtml(
                            result.name
                        )}
                    </h3>


                    <span class="score">
                        ${score}% match
                    </span>

                </div>

                <div class="food-meta">

                    ${escapeHtml(
                        result.cuisine ||
                        "Cuisine"
                    )}

                    ·

                    ${escapeHtml(
                        result.diet_type ||
                        "Food"
                    )}

                </div>

                <div class="food-price">

                    ${price}

                </div>

                <div class="food-nutrition">

                    <span class="nutrition-pill">

                        ${calories}

                    </span>

                    <span class="nutrition-pill">

                        ${protein}

                    </span>

                </div>

                <div class="why-match">

            <div class="why-match-title">
                <span>Why this match</span>
            </div>

            <div class="why-match-list">

                ${reasons}

            </div>

        </div>


        <div
            class="food-feedback"
            data-food-id="${escapeAttribute(result.food_id)}"
            onclick="event.stopPropagation()"
        >

            <span class="feedback-label">
                Was this recommendation useful?
            </span>

            <div class="feedback-buttons">

                <button
                    type="button"
                    class="feedback-button feedback-like"
                    data-feedback="like"
                    onclick="
                        event.stopPropagation();
                        submitRecommendationFeedback(
                            '${escapeAttribute(result.food_id)}',
                            'like'
                        );
                    "
                    aria-label="Good match"
                >
                    👍
                </button>

                <button
                    type="button"
                    class="feedback-button feedback-dislike"
                    data-feedback="dislike"
                    onclick="
                        event.stopPropagation();
                        submitRecommendationFeedback(
                            '${escapeAttribute(result.food_id)}',
                            'dislike'
                        );
                    "
                    aria-label="Not for me"
                >
                    👎
                </button>

            </div>

        </div>


    </div>

        </article>
    `;

}
/* ============================================================
   START OVER
   ============================================================ */

function setupStartOver() {

    const button = document.getElementById(
        "startOverButton"
    );


    if (!button) {
        return;
    }


    button.addEventListener(
        "click",
        () => {

            state.mood = null;

            state.hunger = null;

            state.diet = null;

            state.food_type = null;


            document
                .querySelectorAll(
                    ".option-button.selected"
                )
                .forEach(item => {

                    item.classList.remove(
                        "selected"
                    );

                });


            const resultsSection =
                document.getElementById(
                    "resultsSection"
                );


            if (resultsSection) {

                resultsSection.classList.add(
                    "hidden"
                );

            }


            window.scrollTo({

                top: 0,

                behavior: "smooth",

            });

        }
    );

}


/* ============================================================
   SECURITY HELPERS
   ============================================================ */

function escapeHtml(value) {

    if (
        value === null ||
        value === undefined
    ) {

        return "";

    }


    return String(value)

        .replaceAll(
            "&",
            "&amp;"
        )

        .replaceAll(
            "<",
            "&lt;"
        )

        .replaceAll(
            ">",
            "&gt;"
        )

        .replaceAll(
            '"',
            "&quot;"
        )

        .replaceAll(
            "'",
            "&#039;"
        );

}


function escapeAttribute(value) {

    return escapeHtml(value);

}


/* ============================================================
   OPEN FOOD DETAIL
   ============================================================ */

function openFoodDetail(foodId) {

    if (!foodId) {
        return;
    }


    window.location.href =
        `/food/${encodeURIComponent(foodId)}/`;

}


/* ============================================================
   FOOD DETAIL PAGE
   ============================================================ */

async function loadFoodDetail() {

    const container =
        document.getElementById(
            "foodDetail"
        );


    if (!container) {
        return;
    }


    const pathParts =
        window.location.pathname
            .split("/")
            .filter(Boolean);


    const foodIndex =
        pathParts.indexOf(
            "food"
        );


    if (foodIndex === -1) {
        return;
    }


    const foodId =
        pathParts[foodIndex + 1];


    if (!foodId) {
        return;
    }


    /*
    * Record that the logged-in user
    * opened this food.
    *
    * This is intentionally separate
    * from loading the food details.
    */
    recordFoodView(
        foodId
    );


    try {

        const response =
            await fetch(
                `/api/foods/${encodeURIComponent(foodId)}/`
            );


        const data =
            await response.json();


        if (
            !response.ok ||
            !data.success
        ) {

            throw new Error(
                "Could not load food."
            );

        }


        renderFoodDetail(
            data.food
        );

        renderSimilarFoods(
            data.similar_foods || []
        );

    } catch (error) {

        console.error(error);


        container.innerHTML = `
            <div class="detail-loading">

                Unable to load this food.

                <br>

                <a href="/">
                    Return to Discover
                </a>

            </div>
        `;

    }

}


/* ============================================================
   RENDER FOOD DETAIL
   ============================================================ */

function renderFoodDetail(food) {

    const container =
        document.getElementById(
            "foodDetail"
        );


    if (!container) {
        return;
    }


    const image =
        food.image_url
            ? food.image_url
            : "https://placehold.co/1200x800?text=MoodBite";


    const price =
        food.price &&
        food.price.avg_inr != null

            ? `₹${Math.round(
                food.price.avg_inr
            )}`

            : "Price unavailable";


    const calories =
        food.nutrition &&
        food.nutrition.calories != null

            ? `${Math.round(
                food.nutrition.calories
            )} kcal`

            : "N/A";


    const protein =
        food.nutrition &&
        food.nutrition.protein_g != null

            ? `${Number(
                food.nutrition.protein_g
            ).toFixed(1)} g`

            : "N/A";


    const carbs =
        food.nutrition &&
        food.nutrition.carbs_g != null

            ? `${Number(
                food.nutrition.carbs_g
            ).toFixed(1)} g`

            : "N/A";


    const fat =
        food.nutrition &&
        food.nutrition.fat_g != null

            ? `${Number(
                food.nutrition.fat_g
            ).toFixed(1)} g`

            : "N/A";


    const fiber =
        food.nutrition &&
        food.nutrition.fiber_g != null

            ? `${Number(
                food.nutrition.fiber_g
            ).toFixed(1)} g`

            : "N/A";


    container.innerHTML = `

        <div class="detail-hero">


            <div class="detail-image-wrapper">

                <img
                    src="${escapeAttribute(image)}"

                    alt="${escapeAttribute(
                        food.name
                    )}"

                    class="detail-image"

                    onerror="
                        this.src='https://placehold.co/1200x800?text=MoodBite'
                    "
                >

            </div>


            <div class="detail-info">


                <div class="eyebrow">

                    ${escapeHtml(
                        food.category ||
                        "FOOD"
                    )}

                </div>


                <h1>

                    ${escapeHtml(
                        food.name
                    )}

                </h1>


                <div class="detail-meta">


                    <span>

                        ${escapeHtml(
                            food.cuisine ||
                            "Cuisine"
                        )}

                    </span>


                    <span>•</span>


                    <span>

                        ${escapeHtml(
                            food.diet_type ||
                            "Food"
                        )}

                    </span>


                </div>


                ${
                    food.description

                        ? `
                            <p class="detail-description">

                                ${escapeHtml(
                                    food.description
                                )}

                            </p>
                        `

                        : ""
                }


                <div class="detail-price">

                    ${price}

                </div>


                <button
                    id="saveFoodButton"

                    class="save-food-button"

                    type="button"

                    onclick="
                        handleSaveButton(
                            '${escapeAttribute(
                                food.food_id
                            )}'
                        )
                    "
                >

                    ♡ Save Food

                </button>


            </div>


        </div>


        <div class="nutrition-section">


            <div class="eyebrow">

                NUTRITION

            </div>


            <div class="nutrition-grid">


                <div class="nutrition-card">

                    <strong>
                        ${calories}
                    </strong>

                    <span>
                        Calories
                    </span>

                </div>


                <div class="nutrition-card">

                    <strong>
                        ${protein}
                    </strong>

                    <span>
                        Protein
                    </span>

                </div>


                <div class="nutrition-card">

                    <strong>
                        ${carbs}
                    </strong>

                    <span>
                        Carbs
                    </span>

                </div>


                <div class="nutrition-card">

                    <strong>
                        ${fat}
                    </strong>

                    <span>
                        Fat
                    </span>

                </div>


                <div class="nutrition-card">

                    <strong>
                        ${fiber}
                    </strong>

                    <span>
                        Fiber
                    </span>

                </div>


            </div>


        </div>


        <div class="recipe-content">


            <div class="recipe-column">


                <div class="eyebrow">

                    INGREDIENTS

                </div>


                <div class="ingredients">

                    ${formatIngredients(
                        food.ingredients
                    )}

                </div>


            </div>


            <div class="recipe-column">


                <div class="eyebrow">

                    INSTRUCTIONS

                </div>


                <div class="instructions">

                    ${formatInstructions(
                        food.instructions
                    )}

                </div>


            </div>


        </div>

    `;


    /*
     * After the detail page is rendered,
     * ask Django whether THIS logged-in user
     * has saved THIS food.
     */

    checkAndUpdateSavedButton(
        food.food_id
    );

}


/* ============================================================
   INGREDIENT FORMATTER
   ============================================================ */

function formatIngredients(value) {

    if (!value) {

        return `
            <p>
                Ingredients unavailable.
            </p>
        `;

    }


    if (typeof value === "string") {

        return `
            <p>
                ${escapeHtml(value)}
            </p>
        `;

    }


    return `
        <pre class="ingredients-json">${escapeHtml(
            JSON.stringify(
                value,
                null,
                2
            )
        )}</pre>
    `;

}


/* ============================================================
   INSTRUCTION FORMATTER
   ============================================================ */

function formatInstructions(value) {

    if (!value) {

        return `
            <p>
                Instructions unavailable.
            </p>
        `;

    }


    const steps =
        String(value)
            .split(/\r?\n/)
            .filter(Boolean);


    return steps

        .map(
            (step, index) => `

                <div class="instruction-step">

                    <span>

                        ${index + 1}

                    </span>


                    <p>

                        ${escapeHtml(
                            step
                        )}

                    </p>

                </div>

            `
        )

        .join("");

}


/* ============================================================
   CSRF TOKEN
   ============================================================ */

function getCookie(name) {

    const cookies =
        document.cookie
            ? document.cookie.split(";")
            : [];


    for (
        const cookie of cookies
    ) {

        const trimmed =
            cookie.trim();


        if (
            trimmed.startsWith(
                `${name}=`
            )
        ) {

            return decodeURIComponent(
                trimmed.substring(
                    name.length + 1
                )
            );

        }

    }


    return null;

}


function getCSRFToken() {

    return getCookie(
        "csrftoken"
    );

}


/* ============================================================
   CHECK SAVED STATUS
   ============================================================ */

async function isFoodSaved(foodId) {

    if (!foodId) {
        return false;
    }


    try {

        const response =
            await fetch(
                `/accounts/api/saved-foods/${encodeURIComponent(
                    foodId
                )}/`,
                {
                    method: "GET",

                    credentials:
                        "same-origin",

                    headers: {
                        "Accept":
                            "application/json",
                    },
                }
            );


        /*
         * Django's login_required can redirect
         * an unauthenticated request.
         */

        if (response.redirected) {

            return false;

        }


        if (!response.ok) {

            return false;

        }


        const contentType =
            response.headers.get(
                "content-type"
            ) || "";


        if (
            !contentType.includes(
                "application/json"
            )
        ) {

            return false;

        }


        const data =
            await response.json();


        return (
            data.success === true &&
            data.saved === true
        );


    } catch (error) {

        console.error(
            "Could not check saved food:",
            error
        );


        return false;

    }

}


/* ============================================================
   CHECK AND UPDATE DETAIL BUTTON
   ============================================================ */

async function checkAndUpdateSavedButton(
    foodId
) {

    const button =
        document.getElementById(
            "saveFoodButton"
        );


    if (!button) {
        return;
    }


    const saved =
        await isFoodSaved(
            foodId
        );


    updateSaveButton(
        saved
    );

}


/* ============================================================
   UPDATE SAVE BUTTON
   ============================================================ */

function updateSaveButton(saved) {

    const button =
        document.getElementById(
            "saveFoodButton"
        );


    if (!button) {
        return;
    }


    if (saved) {

        button.classList.add(
            "saved"
        );


        button.innerHTML =
            "♥ Saved";


    } else {

        button.classList.remove(
            "saved"
        );


        button.innerHTML =
            "♡ Save Food";

    }

}


/* ============================================================
   HANDLE SAVE BUTTON
   ============================================================ */

async function handleSaveButton(
    foodId
) {

    if (!foodId) {
        return;
    }


    const saved =
        await isFoodSaved(
            foodId
        );


    if (saved) {

        await removeSavedFood(
            foodId
        );

    } else {

        await saveFood(
            foodId
        );

    }

}


/* ============================================================
   SAVE FOOD
   ============================================================ */

async function saveFood(foodId) {

    if (!foodId) {
        return;
    }


    try {

        const response =
            await fetch(
                `/accounts/api/saved-foods/${encodeURIComponent(
                    foodId
                )}/save/`,
                {
                    method: "POST",

                    credentials:
                        "same-origin",

                    headers: {

                        "X-CSRFToken":
                            getCSRFToken(),

                        "Content-Type":
                            "application/json",

                        "Accept":
                            "application/json",

                    },

                    body: JSON.stringify({}),

                }
            );


        /*
         * If Django redirected to login,
         * the user is not authenticated.
         */

        if (response.redirected) {

            window.location.href =
                "/accounts/login/";

            return;

        }


        const contentType =
            response.headers.get(
                "content-type"
            ) || "";


        if (
            !contentType.includes(
                "application/json"
            )
        ) {

            window.location.href =
                "/accounts/login/";

            return;

        }


        const data =
            await response.json();


        if (
            !response.ok ||
            !data.success
        ) {

            throw new Error(
                data.message ||
                "Could not save food."
            );

        }


        updateSaveButton(
            true
        );


    } catch (error) {

        console.error(
            "Save food error:",
            error
        );


        /*
         * Do not use localStorage.
         *
         * Saved foods belong to the
         * authenticated Django user.
         */

        alert(
            "Please login to save foods."
        );

    }

}


/* ============================================================
   REMOVE SAVED FOOD
   ============================================================ */

async function removeSavedFood(
    foodId
) {

    if (!foodId) {
        return;
    }


    try {

        const response =
            await fetch(
                `/accounts/api/saved-foods/${encodeURIComponent(
                    foodId
                )}/remove/`,
                {
                    method: "POST",

                    credentials:
                        "same-origin",

                    headers: {

                        "X-CSRFToken":
                            getCSRFToken(),

                        "Content-Type":
                            "application/json",

                        "Accept":
                            "application/json",

                    },

                    body: JSON.stringify({}),

                }
            );


        if (response.redirected) {

            window.location.href =
                "/accounts/login/";

            return;

        }


        const contentType =
            response.headers.get(
                "content-type"
            ) || "";


        if (
            !contentType.includes(
                "application/json"
            )
        ) {

            throw new Error(
                "Invalid server response."
            );

        }


        const data =
            await response.json();


        if (
            !response.ok ||
            !data.success
        ) {

            throw new Error(
                data.message ||
                "Could not remove food."
            );

        }


        /*
         * If we're on the Saved Foods page,
         * reload only this user's saved foods.
         */

        const savedGrid =
            document.getElementById(
                "savedFoodsGrid"
            );


        if (savedGrid) {

            await loadSavedFoodsPage();

        } else {

            updateSaveButton(
                false
            );

        }


    } catch (error) {

        console.error(
            "Remove saved food error:",
            error
        );

    }

}


/* ============================================================
   SAVED FOODS PAGE
   ============================================================ */

async function loadSavedFoodsPage() {

    const grid =
        document.getElementById(
            "savedFoodsGrid"
        );


    /*
     * This function is only active
     * on the Saved Foods page.
     */

    if (!grid) {
        return;
    }


    grid.innerHTML = `
        <div class="loading">
            Loading your saved foods...
        </div>
    `;


    try {

        const response =
            await fetch(
                "/accounts/api/saved-foods/",
                {
                    method: "GET",

                    credentials:
                        "same-origin",

                    headers: {
                        "Accept":
                            "application/json",
                    },
                }
            );


        /*
         * Django authentication redirect.
         */

        if (response.redirected) {

            window.location.href =
                "/accounts/login/";

            return;

        }


        const contentType =
            response.headers.get(
                "content-type"
            ) || "";


        if (
            !contentType.includes(
                "application/json"
            )
        ) {

            window.location.href =
                "/accounts/login/";

            return;

        }


        const data =
            await response.json();


        if (
            !response.ok ||
            !data.success
        ) {

            throw new Error(
                data.message ||
                "Could not load saved foods."
            );

        }


        /*
         * IMPORTANT:
         *
         * The server returns ONLY foods
         * belonging to request.user.
         *
         * There is no localStorage here.
         */

        const foods =
            data.foods || [];


        /*
         * NOTHING SAVED
         */

        if (!foods.length) {

            grid.innerHTML = `
                <div class="saved-empty">

                    <div class="saved-empty-icon">
                        ♡
                    </div>

                    <h2>
                        Nothing saved yet.
                    </h2>

                    <p>
                        When you find something you love,
                        save it here.
                    </p>

                    <a
                        href="/"
                        class="discover-button"
                    >
                        Find My Food →
                    </a>

                </div>
            `;

            return;

        }


        /*
         * RENDER ONLY THE LOGGED-IN
         * USER'S SAVED FOODS.
         */

        grid.innerHTML =
            foods
                .map(
                    food =>
                        createSavedFoodCard(
                            food
                        )
                )
                .join("");


    } catch (error) {

        console.error(
            "Saved foods error:",
            error
        );


        grid.innerHTML = `
            <div class="saved-empty">

                <h2>
                    Something went wrong.
                </h2>

                <p>
                    Please refresh the page
                    and try again.
                </p>

            </div>
        `;

    }

}


/* ============================================================
   SAVED FOOD CARD
   ============================================================ */

function createSavedFoodCard(food) {

    const image =
        food.image_url
            ? food.image_url
            : "https://placehold.co/800x600?text=MoodBite";


    const price =
        food.price &&
        food.price.avg_inr != null

            ? `₹${Math.round(
                food.price.avg_inr
            )}`

            : "Price unavailable";


    const calories =
        food.nutrition &&
        food.nutrition.calories != null

            ? `${Math.round(
                food.nutrition.calories
            )} kcal`

            : "Calories N/A";


    const protein =
        food.nutrition &&
        food.nutrition.protein_g != null

            ? `${Number(
                food.nutrition.protein_g
            ).toFixed(1)}g protein`

            : "Protein N/A";


    return `
        <article
            class="food-card saved-food-card"
        >


            <div
                class="saved-card-image-wrapper"

                onclick="openFoodDetail(
                    '${escapeAttribute(
                        food.food_id
                    )}'
                )"
            >

                <img
                    class="food-image"

                    src="${escapeAttribute(
                        image
                    )}"

                    alt="${escapeAttribute(
                        food.name
                    )}"

                    loading="lazy"

                    onerror="
                        this.src='https://placehold.co/800x600?text=MoodBite'
                    "
                >

            </div>


            <div class="food-card-content">


                <div class="food-card-top">


                    <h3
                        onclick="openFoodDetail(
                            '${escapeAttribute(
                                food.food_id
                            )}'
                        )"
                    >

                        ${escapeHtml(
                            food.name
                        )}

                    </h3>


                    <span class="saved-badge">

                        ♥ Saved

                    </span>


                </div>


                <div class="food-meta">

                    ${escapeHtml(
                        food.cuisine ||
                        "Cuisine"
                    )}

                    ·

                    ${escapeHtml(
                        food.diet_type ||
                        "Food"
                    )}

                </div>


                <div class="food-price">

                    ${price}

                </div>


                <div class="food-nutrition">


                    <span class="nutrition-pill">

                        ${calories}

                    </span>


                    <span class="nutrition-pill">

                        ${protein}

                    </span>


                </div>


                <div class="saved-card-actions">


                    <button
                        type="button"

                        class="view-food-button"

                        onclick="openFoodDetail(
                            '${escapeAttribute(
                                food.food_id
                            )}'
                        )"
                    >

                        View Food →

                    </button>


                    <button
                        type="button"

                        class="remove-saved-button"

                        onclick="removeSavedFood(
                            '${escapeAttribute(
                                food.food_id
                            )}'
                        )"
                    >

                        Remove

                    </button>


                </div>


            </div>


        </article>
    `;

}


/* ============================================================
   LOAD DETAIL PAGE
   ============================================================ */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        loadFoodDetail();

        loadSavedFoodsPage();

    }
);
/* ============================================================
   RECOMMENDATION HISTORY
   ============================================================ */

async function loadRecommendationHistory() {

    const container = document.getElementById(
        "historyContainer"
    );

    if (!container) {
        return;
    }

    try {

        const response = await fetch(
            "/accounts/api/history/",
            {
                method: "GET",
                credentials: "same-origin",
                headers: {
                    "Accept": "application/json",
                },
            }
        );

        /*
         * Django login protection may redirect
         * unauthenticated users to the login page.
         */

        if (response.redirected) {

            window.location.href =
                "/accounts/login/?next=/accounts/history/";

            return;
        }

        const contentType =
            response.headers.get("content-type") || "";

        if (!contentType.includes("application/json")) {

            window.location.href =
                "/accounts/login/?next=/accounts/history/";

            return;
        }

        const data = await response.json();

        if (!data.success) {

            container.innerHTML = `
                <div class="history-error">
                    <h2>Unable to load history</h2>
                    <p>Please try again.</p>
                </div>
            `;

            return;
        }

        renderRecommendationHistory(
            data.history || []
        );

    } catch (error) {

        console.error(
            "History loading error:",
            error
        );

        container.innerHTML = `
            <div class="history-error">
                <h2>Something went wrong</h2>
                <p>
                    We couldn't load your recommendation history.
                    Please refresh the page.
                </p>
            </div>
        `;
    }
}


/* ============================================================
   RENDER HISTORY
   ============================================================ */

function renderRecommendationHistory(
    history
) {

    const container = document.getElementById(
        "historyContainer"
    );

    if (!container) {
        return;
    }

    if (!history.length) {

        container.innerHTML = `
            <div class="history-empty">

                <div class="history-empty-icon">
                    🕘
                </div>

                <h2>
                    No recommendation history yet
                </h2>

                <p>
                    Start discovering food and your
                    recommendation sessions will appear here.
                </p>

                <a
                    href="/"
                    class="discover-button"
                >
                    Discover Food →
                </a>

            </div>
        `;

        return;
    }

    container.innerHTML = history
        .map(
            item => createHistoryCard(item)
        )
        .join("");
}


/* ============================================================
   HISTORY CARD
   ============================================================ */
function createHistoryCard(
    item
) {

    const date = formatHistoryDate(
        item.created_at
    );

    const mood =
        item.mood || "Not specified";

    const hunger =
        item.hunger || "Not specified";

    const foodType =
        item.food_type || "Not specified";

    const diet =
        item.diet_type || "Not specified";

    const budget =
        item.budget !== null &&
        item.budget !== undefined
            ? `₹${Number(
                item.budget
            ).toLocaleString("en-IN")}`
            : "No budget";


    const foods =
        Array.isArray(item.results)
            ? item.results
            : [];


    const foodList = foods
        .slice(0, 5)
        .map(
            food => {

                const foodId =
                    food.food_id || "";

                const foodName =
                    food.name ||
                    "Unknown food";

                const clickable =
                    Boolean(foodId);


                return `
                    <div
                        class="history-food ${
                            clickable
                                ? "history-food-clickable"
                                : ""
                        }"
                        ${
                            clickable
                                ? `
                                    onclick="openFoodDetail(
                                        '${escapeAttribute(
                                            foodId
                                        )}'
                                    )"
                                    role="button"
                                    tabindex="0"
                                    onkeydown="
                                        if (
                                            event.key === 'Enter' ||
                                            event.key === ' '
                                        ) {
                                            openFoodDetail(
                                                '${escapeAttribute(
                                                    foodId
                                                )}'
                                            );
                                        }
                                    "
                                `
                                : ""
                        }
                    >

                        <div class="history-food-name">

                            ${
                                clickable
                                    ? `
                                        <span
                                            class="history-food-link"
                                        >
                                            ${escapeHistoryHTML(
                                                foodName
                                            )}
                                        </span>
                                    `
                                    : `
                                        ${escapeHistoryHTML(
                                            foodName
                                        )}
                                    `
                            }

                        </div>


                        ${
                            food.score !== undefined
                                ? `
                                    <span
                                        class="history-score"
                                    >
                                        ${formatHistoryScore(
                                            food.score
                                        )}
                                    </span>
                                `
                                : ""
                        }

                    </div>
                `;
            }
        )
        .join("");


    const extraCount =
        foods.length > 5
            ? foods.length - 5
            : 0;


    return `
        <article class="history-card">

            <div class="history-card-header">

                <div>

                    <span class="history-date">
                        ${date}
                    </span>

                    <h2>
                        ${escapeHistoryHTML(
                            capitalizeHistoryText(
                                mood
                            )
                        )}
                        mood
                    </h2>

                </div>


                <span class="history-count">

                    ${foods.length}

                    ${
                        foods.length === 1
                            ? " recommendation"
                            : " recommendations"
                    }

                </span>

            </div>


            <div class="history-filters">

                <div class="history-filter">

                    <span>
                        Mood
                    </span>

                    <strong>
                        ${escapeHistoryHTML(
                            capitalizeHistoryText(
                                mood
                            )
                        )}
                    </strong>

                </div>


                <div class="history-filter">

                    <span>
                        Hunger
                    </span>

                    <strong>
                        ${escapeHistoryHTML(
                            capitalizeHistoryText(
                                hunger
                            )
                        )}
                    </strong>

                </div>


                <div class="history-filter">

                    <span>
                        Food Type
                    </span>

                    <strong>
                        ${escapeHistoryHTML(
                            capitalizeHistoryText(
                                foodType
                            )
                        )}
                    </strong>

                </div>


                <div class="history-filter">

                    <span>
                        Diet
                    </span>

                    <strong>
                        ${escapeHistoryHTML(
                            capitalizeHistoryText(
                                diet
                            )
                        )}
                    </strong>

                </div>


                <div class="history-filter">

                    <span>
                        Budget
                    </span>

                    <strong>
                        ${budget}
                    </strong>

                </div>

            </div>


            <div class="history-foods">

                <div class="history-foods-title">
                    Recommended foods
                </div>


                ${
                    foodList ||
                    `
                        <p class="history-no-foods">
                            No recommendation details stored.
                        </p>
                    `
                }


                ${
                    extraCount > 0
                        ? `
                            <div class="history-more">
                                +${extraCount}
                                more
                            </div>
                        `
                        : ""
                }

            </div>

        </article>
    `;
}


/* ============================================================
   HISTORY DATE
   ============================================================ */

function formatHistoryDate(
    value
) {

    if (!value) {
        return "Unknown date";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
        return "Unknown date";
    }

    return date.toLocaleString(
        "en-IN",
        {
            day: "numeric",
            month: "short",
            year: "numeric",
            hour: "numeric",
            minute: "2-digit",
        }
    );
}


/* ============================================================
   HISTORY SCORE
   ============================================================ */

function formatHistoryScore(
    score
) {

    const numericScore =
        Number(score);

    if (!Number.isFinite(numericScore)) {
        return "";
    }

    return `${numericScore.toFixed(1)} score`;
}


/* ============================================================
   HISTORY TEXT HELPERS
   ============================================================ */

function capitalizeHistoryText(
    value
) {

    if (!value) {
        return "";
    }

    return String(value)
        .replace(/_/g, " ")
        .replace(/\b\w/g, char =>
            char.toUpperCase()
        );
}


function escapeHistoryHTML(
    value
) {

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


/* ============================================================
   CLEAR HISTORY
   ============================================================ */

async function clearRecommendationHistory() {

    const button = document.getElementById(
        "clearHistoryButton"
    );

    if (!button) {
        return;
    }

    const confirmed = window.confirm(
        "Are you sure you want to clear your recommendation history?"
    );

    if (!confirmed) {
        return;
    }


    try {

        button.disabled = true;

        button.textContent =
            "Clearing...";


        const response = await fetch(
            "/accounts/api/history/clear/",
            {
                method: "POST",

                credentials: "same-origin",

                headers: {
                    "X-CSRFToken":
                        getCSRFToken(),

                    "Accept":
                        "application/json",
                },
            }
        );


        if (response.redirected) {

            window.location.href =
                "/accounts/login/?next=/accounts/history/";

            return;
        }


        const data =
            await response.json();


        if (!data.success) {

            throw new Error(
                data.message ||
                "Unable to clear history."
            );
        }


        renderRecommendationHistory(
            []
        );


    } catch (error) {

        console.error(
            "History clear error:",
            error
        );

        alert(
            "Unable to clear your history. Please try again."
        );

    } finally {

        button.disabled = false;

        button.textContent =
            "Clear History";
    }
}


/* ============================================================
   HISTORY PAGE INITIALIZATION
   ============================================================ */

document.addEventListener(
    "DOMContentLoaded",
    () => {

        loadRecommendationHistory();

        const clearButton =
            document.getElementById(
                "clearHistoryButton"
            );

        if (clearButton) {

            clearButton.addEventListener(
                "click",
                clearRecommendationHistory
            );
        }

    }
);
/* ============================================================
   USER PREFERENCES
   ============================================================ */

async function loadUserPreferences() {

    const form = document.getElementById("preferencesForm");

    if (!form) {
        return;
    }

    try {

        const response = await fetch(
            "/accounts/api/preferences/",
            {
                method: "GET",
                credentials: "same-origin",
            }
        );

        if (response.status === 401) {
            window.location.href =
                "/accounts/login/?next=/accounts/preferences/";
            return;
        }

        const data = await response.json();

        if (!data.success) {
            return;
        }

        const preferences = data.preferences;

        const foodType =
            document.getElementById(
                "preferredFoodType"
            );

        const dietType =
            document.getElementById(
                "preferredDietType"
            );

        const cuisine =
            document.getElementById(
                "preferredCuisine"
            );

        const budget =
            document.getElementById(
                "preferredBudget"
            );

        if (foodType) {
            foodType.value =
                preferences.preferred_food_type || "";
        }

        if (dietType) {
            dietType.value =
                preferences.preferred_diet_type || "";
        }

        if (cuisine) {
            cuisine.value =
                preferences.preferred_cuisine || "";
        }

        if (
            budget &&
            preferences.preferred_budget !== null
        ) {
            budget.value =
                preferences.preferred_budget;
        }

    } catch (error) {

        console.error(
            "Failed to load preferences:",
            error
        );
    }
}


async function saveUserPreferences(event) {

    event.preventDefault();

    const button =
        document.getElementById(
            "savePreferencesButton"
        );

    const message =
        document.getElementById(
            "preferencesMessage"
        );

    const form =
        document.getElementById(
            "preferencesForm"
        );

    if (!form) {
        return;
    }

    const formData =
        new FormData(form);

    if (button) {
        button.disabled = true;
        button.textContent = "Saving...";
    }

    if (message) {
        message.textContent = "";
        message.className =
            "preferences-message";
    }

    try {

        const response = await fetch(
            "/accounts/api/preferences/update/",
            {
                method: "POST",
                body: formData,
                credentials: "same-origin",
                headers: {
                    "X-CSRFToken":
                        getCSRFToken(),
                },
            }
        );

        const data =
            await response.json();

        if (!response.ok || !data.success) {

            throw new Error(
                data.message ||
                "Unable to save preferences."
            );
        }

        if (message) {

            message.textContent =
                "Preferences saved successfully.";

            message.className =
                "preferences-message success";
        }

        if (button) {
            button.textContent =
                "Saved ✓";
        }

    } catch (error) {

        console.error(
            "Failed to save preferences:",
            error
        );

        if (message) {

            message.textContent =
                error.message ||
                "Something went wrong.";

            message.className =
                "preferences-message error";
        }

        if (button) {
            button.textContent =
                "Save Preferences →";
        }

    } finally {

        if (button) {

            setTimeout(() => {

                button.disabled = false;

                if (
                    button.textContent ===
                    "Saved ✓"
                ) {
                    button.textContent =
                        "Save Preferences →";
                }

            }, 1500);
        }
    }
}


document.addEventListener(
    "DOMContentLoaded",
    () => {

        const form =
            document.getElementById(
                "preferencesForm"
            );

        if (!form) {
            return;
        }

        loadUserPreferences();

        form.addEventListener(
            "submit",
            saveUserPreferences
        );
    }
);

/* ============================================================
   FOOD DISCOVERY / SEARCH
   ============================================================ */

document.addEventListener(
    "DOMContentLoaded",
    () => {
        setupFoodDiscovery();
    }
);


function setupFoodDiscovery() {

    const resultsSection =
        document.getElementById(
            "resultsSection"
        );

    if (!resultsSection) {
        return;
    }

    if (
        document.getElementById(
            "foodDiscoverySection"
        )
    ) {
        return;
    }

    const section =
        document.createElement("section");

    section.id =
        "foodDiscoverySection";

    section.className =
        "food-discovery-section";


    section.innerHTML = `
        <div class="compact-search-header">

            <div class="eyebrow">
                EXPLORE THE COLLECTION
            </div>

            <h2>
                Find your next
                <span>favourite.</span>
            </h2>

        </div>


        <div class="food-search-panel compact-food-search-panel">

            <div class="food-search-main">

                <label
                    for="foodSearchInput"
                >
                    SEARCH FOOD
                </label>

                <div class="food-search-input-wrap">

                    <input
                        type="search"
                        id="foodSearchInput"
                        placeholder="Search biryani, paneer, curry..."
                        autocomplete="off"
                    >

                    <button
                        type="button"
                        id="foodSearchButton"
                    >
                        Search →
                    </button>

                </div>

            </div>


            <div class="food-search-filters compact-search-filters">

                <div class="search-filter">

                    <label
                        for="searchFoodType"
                    >
                        FOOD TYPE
                    </label>

                    <select
                        id="searchFoodType"
                    >

                        <option value="">
                            All food
                        </option>

                        <option value="Indian">
                            Indian
                        </option>

                        <option value="International">
                            International
                        </option>

                    </select>

                </div>


                <div class="search-filter">

                    <label
                        for="searchDiet"
                    >
                        DIET
                    </label>

                    <select
                        id="searchDiet"
                    >

                        <option value="">
                            All diets
                        </option>

                        <option value="Vegetarian">
                            Vegetarian
                        </option>

                        <option value="Vegan">
                            Vegan
                        </option>

                        <option value="Non-Vegetarian">
                            Non-Vegetarian
                        </option>

                    </select>

                </div>


                <div class="search-filter">

                    <label
                        for="searchCuisine"
                    >
                        CUISINE
                    </label>

                    <input
                        type="text"
                        id="searchCuisine"
                        placeholder="e.g. Punjabi"
                    >

                </div>


                <div class="search-filter">

                    <label
                        for="searchMaxPrice"
                    >
                        MAX PRICE
                    </label>

                    <input
                        type="number"
                        id="searchMaxPrice"
                        min="1"
                        placeholder="₹500"
                    >

                </div>


                <div class="search-filter">

                    <label
                        for="searchMaxCalories"
                    >
                        MAX CALORIES
                    </label>

                    <input
                        type="number"
                        id="searchMaxCalories"
                        min="1"
                        placeholder="600"
                    >

                </div>


                <div class="search-filter">

                    <label
                        for="searchMinProtein"
                    >
                        MIN PROTEIN
                    </label>

                    <input
                        type="number"
                        id="searchMinProtein"
                        min="0"
                        step="0.1"
                        placeholder="10g"
                    >

                </div>

            </div>


            <div class="food-search-actions compact-search-actions">

                <button
                    type="button"
                    id="foodSearchButtonSecondary"
                    class="food-search-button"
                >
                    Search Foods →
                </button>

                <button
                    type="button"
                    id="clearFoodSearch"
                    class="food-search-clear"
                >
                    Clear filters
                </button>

            </div>

        </div>


        <div
            id="foodSearchStatus"
            class="food-search-status"
        ></div>


        <div
            id="foodSearchResults"
            class="food-search-results"
        ></div>
    `;


    /*
     * Put Search at the top of the main
     * MoodBite experience.
     */

    const mainElement =
        document.querySelector("main");


    if (mainElement) {

        mainElement.insertBefore(
            section,
            mainElement.firstElementChild
        );

    } else {

        /*
         * Safe fallback.
         */

        resultsSection.parentNode.insertBefore(
            section,
            resultsSection
        );

    }


    setupFoodSearchControls();
}


/* ============================================================
   SEARCH CONTROLS
   ============================================================ */

function setupFoodSearchControls() {

    const primaryButton =
        document.getElementById(
            "foodSearchButton"
        );

    const secondaryButton =
        document.getElementById(
            "foodSearchButtonSecondary"
        );

    const clearButton =
        document.getElementById(
            "clearFoodSearch"
        );

    const input =
        document.getElementById(
            "foodSearchInput"
        );


    if (primaryButton) {

        primaryButton.addEventListener(
            "click",
            searchMoodBiteFoods
        );

    }


    if (secondaryButton) {

        secondaryButton.addEventListener(
            "click",
            searchMoodBiteFoods
        );

    }


    if (clearButton) {

        clearButton.addEventListener(
            "click",
            clearFoodSearch
        );

    }


    if (input) {

        input.addEventListener(
            "keydown",
            event => {

                if (
                    event.key === "Enter"
                ) {

                    event.preventDefault();

                    searchMoodBiteFoods();

                }

            }
        );

    }

}


/* ============================================================
   SEARCH API
   ============================================================ */

async function searchMoodBiteFoods() {

    const input =
        document.getElementById(
            "foodSearchInput"
        );

    const foodType =
        document.getElementById(
            "searchFoodType"
        );

    const diet =
        document.getElementById(
            "searchDiet"
        );

    const cuisine =
        document.getElementById(
            "searchCuisine"
        );

    const maxPrice =
        document.getElementById(
            "searchMaxPrice"
        );

    const maxCalories =
        document.getElementById(
            "searchMaxCalories"
        );

    const minProtein =
        document.getElementById(
            "searchMinProtein"
        );

    const status =
        document.getElementById(
            "foodSearchStatus"
        );

    const results =
        document.getElementById(
            "foodSearchResults"
        );


    if (
        !input ||
        !foodType ||
        !diet ||
        !cuisine ||
        !maxPrice ||
        !maxCalories ||
        !minProtein ||
        !status ||
        !results
    ) {

        return;

    }


    const query =
        input.value.trim();


    /*
     * At least one search/filter must
     * be provided.
     */

    const hasFilter =
        query ||
        foodType.value ||
        diet.value ||
        cuisine.value.trim() ||
        maxPrice.value ||
        maxCalories.value ||
        minProtein.value;


    if (!hasFilter) {

        status.textContent =
            "Enter a food name or choose a filter.";

        results.innerHTML = "";

        return;

    }


    const params =
        new URLSearchParams();


    if (query) {

        params.set(
            "q",
            query
        );

    }


    if (foodType.value) {

        params.set(
            "food_type",
            foodType.value
        );

    }


    if (diet.value) {

        params.set(
            "diet",
            diet.value
        );

    }


    if (cuisine.value.trim()) {

        params.set(
            "cuisine",
            cuisine.value.trim()
        );

    }


    if (maxPrice.value) {

        params.set(
            "max_price",
            maxPrice.value
        );

    }


    if (maxCalories.value) {

        params.set(
            "max_calories",
            maxCalories.value
        );

    }


    if (minProtein.value) {

        params.set(
            "min_protein",
            minProtein.value
        );

    }


    params.set(
        "limit",
        "24"
    );


    status.textContent =
        "Finding foods...";


    results.innerHTML = `
        <div class="food-search-loading">
            Searching the MoodBite collection...
        </div>
    `;


    try {

        const response =
            await fetch(
                `/api/foods/search/?${params.toString()}`
            );


        const data =
            await response.json();


        if (
            !response.ok ||
            !data.success
        ) {

            throw new Error(
                "Food search failed."
            );

        }


        renderFoodSearchResults(
            data.results
        );


    } catch (error) {

        console.error(
            "MoodBite food search error:",
            error
        );


        status.textContent =
            "Something went wrong while searching.";


        results.innerHTML = `
            <div class="food-search-empty">
                Please try again.
            </div>
        `;

    }

}


/* ============================================================
   SEARCH RESULTS
   ============================================================ */

function renderFoodSearchResults(
    foods
) {

    const status =
        document.getElementById(
            "foodSearchStatus"
        );

    const results =
        document.getElementById(
            "foodSearchResults"
        );


    if (
        !status ||
        !results
    ) {

        return;

    }


    status.textContent =
        `${foods.length} food${
            foods.length === 1
                ? ""
                : "s"
        } found`;


    if (
        !foods ||
        !foods.length
    ) {

        results.innerHTML = `
            <div class="food-search-empty">

                <h3>
                    No matching foods.
                </h3>

                <p>
                    Try another search or
                    relax one of your filters.
                </p>

            </div>
        `;

        return;

    }


    results.innerHTML =
        foods
            .map(
                createDiscoveryFoodCard
            )
            .join("");


    /*
     * Move the results into view.
     */

    results.scrollIntoView({
        behavior: "smooth",
        block: "start",
    });

}


/* ============================================================
   DISCOVERY FOOD CARD
   ============================================================ */

function createDiscoveryFoodCard(
    food
) {

    const image =
        food.image_url
            ? food.image_url
            : "https://placehold.co/800x600?text=MoodBite";


    const price =
        food.price &&
        food.price.avg_inr != null
            ? `₹${Math.round(
                food.price.avg_inr
            )}`
            : "Price unavailable";


    const calories =
        food.nutrition &&
        food.nutrition.calories != null
            ? `${Math.round(
                food.nutrition.calories
            )} kcal`
            : "Calories N/A";


    const protein =
        food.nutrition &&
        food.nutrition.protein_g != null
            ? `${Number(
                food.nutrition.protein_g
            ).toFixed(1)}g protein`
            : "Protein N/A";


    return `
        <article
            class="food-card discovery-food-card"
            onclick="openFoodDetail(
                '${escapeAttribute(food.food_id)}'
            )"
            role="button"
            tabindex="0"
        >

            <img
                class="food-image"
                src="${escapeAttribute(image)}"
                alt="${escapeAttribute(
                    food.name
                )}"
                loading="lazy"
                onerror="
                    this.src='https://placehold.co/800x600?text=MoodBite'
                "
            >

            <div class="food-card-content">

                <div class="food-card-top">

                    <h3>
                        ${escapeHtml(
                            food.name
                        )}
                    </h3>

                </div>


                <div class="food-meta">

                    ${escapeHtml(
                        food.cuisine ||
                        "Cuisine"
                    )}

                    ·

                    ${escapeHtml(
                        food.diet_type ||
                        "Food"
                    )}

                </div>


                <div class="food-price">
                    ${price}
                </div>


                <div class="food-nutrition">

                    <span class="nutrition-pill">
                        ${calories}
                    </span>

                    <span class="nutrition-pill">
                        ${protein}
                    </span>

                </div>


                <div class="discovery-card-action">
                    View Food →
                </div>

            </div>

        </article>
    `;
}


/* ============================================================
   CLEAR SEARCH
   ============================================================ */

function clearFoodSearch() {

    const ids = [
        "foodSearchInput",
        "searchCuisine",
        "searchMaxPrice",
        "searchMaxCalories",
        "searchMinProtein",
    ];


    ids.forEach(
        id => {

            const element =
                document.getElementById(
                    id
                );

            if (element) {

                element.value = "";

            }

        }
    );


    [
        "searchFoodType",
        "searchDiet",
    ].forEach(
        id => {

            const element =
                document.getElementById(
                    id
                );

            if (element) {

                element.value = "";

            }

        }
    );


    const status =
        document.getElementById(
            "foodSearchStatus"
        );

    const results =
        document.getElementById(
            "foodSearchResults"
        );


    if (status) {

        status.textContent = "";

    }


    if (results) {

        results.innerHTML = "";

    }

}
/* ============================================================
   SIMILAR FOODS
   ============================================================ */

function renderSimilarFoods(similarFoods) {

    const detailContainer =
        document.getElementById(
            "foodDetail"
        );

    if (!detailContainer) {
        return;
    }


    /*
     * Remove an existing section first.
     *
     * This prevents duplicate sections if the
     * detail renderer is called more than once.
     */

    const existingSection =
        document.getElementById(
            "similarFoodsSection"
        );

    if (existingSection) {
        existingSection.remove();
    }


    /*
     * If there are no similar foods,
     * don't show an empty section.
     */

    if (
        !Array.isArray(similarFoods) ||
        !similarFoods.length
    ) {
        return;
    }


    const cards = similarFoods
        .map(
            (food) => {

                const image =
                    food.image_url
                        ? food.image_url
                        : "https://placehold.co/600x400?text=MoodBite";


                const price =
                    food.price &&
                    food.price.avg_inr != null

                        ? `₹${Math.round(
                            food.price.avg_inr
                        )}`

                        : "Price unavailable";


                const calories =
                    food.nutrition &&
                    food.nutrition.calories != null

                        ? `${Math.round(
                            food.nutrition.calories
                        )} kcal`

                        : "N/A";


                const similarity =
                    food.similarity != null

                        ? `${Math.round(
                            food.similarity
                        )}% match`

                        : "";


                return `
                    <article
                        class="similar-food-card"
                        onclick="openFoodDetail(
                            '${escapeAttribute(
                                food.food_id
                            )}'
                        )"
                    >

                        <div
                            class="similar-food-image-wrapper"
                        >

                            <img
                                src="${escapeAttribute(
                                    image
                                )}"
                                alt="${escapeAttribute(
                                    food.name
                                )}"
                                class="similar-food-image"
                                loading="lazy"
                                onerror="this.src='https://placehold.co/600x400?text=MoodBite'"
                            >

                        </div>


                        <div
                            class="similar-food-content"
                        >

                            <div
                                class="similar-food-meta"
                            >

                                ${
                                    food.food_type
                                        ? escapeHtml(
                                            food.food_type
                                        )
                                        : ""
                                }

                                ${
                                    food.cuisine
                                        ? ` · ${escapeHtml(
                                            food.cuisine
                                        )}`
                                        : ""
                                }

                            </div>


                            <h3>
                                ${escapeHtml(
                                    food.name
                                )}
                            </h3>


                            <div
                                class="similar-food-info"
                            >

                                <span>
                                    ${price}
                                </span>

                                <span>
                                    ${calories}
                                </span>

                            </div>


                            ${
                                similarity
                                    ? `
                                        <div
                                            class="similar-food-match"
                                        >
                                            ${similarity}
                                        </div>
                                    `
                                    : ""
                            }

                        </div>

                    </article>
                `;
            }
        )
        .join("");


    /*
     * Insert the section directly after
     * the existing food detail container.
     */

    detailContainer.insertAdjacentHTML(
        "afterend",
        `
            <section
                id="similarFoodsSection"
                class="similar-foods-section"
            >

                <div
                    class="similar-foods-header"
                >

                    <div>

                        <div
                            class="eyebrow"
                        >
                            YOU MAY ALSO LIKE
                        </div>

                        <h2>
                            Similar <span>foods.</span>
                        </h2>

                        <p>
                            More dishes that match
                            this food's taste,
                            cuisine and profile.
                        </p>

                    </div>

                </div>


                <div
                    class="similar-foods-grid"
                >
                    ${cards}
                </div>

            </section>
        `
    );

}
/* ============================================================
   RECOMMENDATION FEEDBACK
   ============================================================ */

async function submitRecommendationFeedback(
    foodId,
    feedback
) {

    if (!foodId) {
        return;
    }

    if (
        feedback !== "like" &&
        feedback !== "dislike"
    ) {
        return;
    }

    try {

        const response = await fetch(
            `/accounts/api/feedback/${encodeURIComponent(
                foodId
            )}/save/`,
            {
                method: "POST",

                credentials: "same-origin",

                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCSRFToken(),
                    "X-Requested-With": "XMLHttpRequest"
                },

                body: JSON.stringify({
                    feedback: feedback
                })
            }
        );


        const data =
            await response.json();


        if (
            response.status === 401 ||
            response.status === 403
        ) {

            window.location.href =
                `/accounts/login/?next=${encodeURIComponent(
                    window.location.pathname
                )}`;

            return;
        }


        if (!response.ok || !data.success) {

            throw new Error(
                data.message ||
                "Could not save feedback."
            );

        }


        updateFeedbackButtons(
            foodId,
            feedback
        );


    } catch (error) {

        console.error(
            "Recommendation feedback error:",
            error
        );

    }
}


/* ============================================================
   LOAD EXISTING FEEDBACK
   ============================================================ */

async function loadRecommendationFeedback(
    foodId
) {

    if (!foodId) {
        return;
    }

    try {

        const response = await fetch(
            `/accounts/api/feedback/${encodeURIComponent(
                foodId
            )}/`,
            {
                method: "GET",
                credentials: "same-origin",
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            }
        );


        if (
            response.status === 401 ||
            response.status === 403
        ) {
            return;
        }


        if (!response.ok) {
            return;
        }


        const data =
            await response.json();


        if (
            data.success &&
            data.feedback
        ) {

            updateFeedbackButtons(
                foodId,
                data.feedback
            );

        }


    } catch (error) {

        console.error(
            "Could not load recommendation feedback:",
            error
        );

    }
}


/* ============================================================
   UPDATE FEEDBACK BUTTON STATE
   ============================================================ */

function updateFeedbackButtons(
    foodId,
    feedback
) {

    const container =
        document.querySelector(
            `.food-feedback[data-food-id="${CSS.escape(
                foodId
            )}"]`
        );


    if (!container) {
        return;
    }


    const buttons =
        container.querySelectorAll(
            ".feedback-button"
        );


    buttons.forEach(
        button => {

            button.classList.remove(
                "active"
            );


            if (
                button.dataset.feedback ===
                feedback
            ) {

                button.classList.add(
                    "active"
                );

            }

        }
    );

}
/* ============================================================
   FOOD VIEW TRACKING
   ============================================================ */

async function recordFoodView(
    foodId
) {

    if (!foodId) {
        return;
    }


    try {

        const response =
            await fetch(
                `/accounts/api/food-views/${encodeURIComponent(
                    foodId
                )}/`,
                {
                    method: "POST",

                    credentials:
                        "same-origin",

                    headers: {
                        "X-CSRFToken":
                            getCSRFToken(),

                        "Content-Type":
                            "application/json",

                        "Accept":
                            "application/json",

                    },

                    body: JSON.stringify({}),

                }
            );


        /*
         * A logged-out visitor simply
         * won't have a tracked view.
         *
         * Do not interrupt the food
         * detail page for this.
         */

        if (!response.ok) {

            console.warn(
                "Food view was not recorded:",
                response.status
            );

            return;

        }


        const data =
            await response.json();


        if (
            !data.success
        ) {

            console.warn(
                "Food view was not recorded:",
                data.message
            );

        }


    } catch (error) {

        /*
         * Tracking must never prevent
         * the food detail page from loading.
         */

        console.error(
            "Food view tracking error:",
            error
        );

    }

}