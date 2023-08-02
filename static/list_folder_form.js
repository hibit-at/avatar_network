// @ts-check

document.addEventListener("DOMContentLoaded", () => {
    /**
     * @param {HTMLDivElement} $container 
     */
    function setupButtonContainer($container) {
        const $parentButton = /** @type {HTMLButtonElement} */($container.querySelector(".list_folder_button"));
        const $forms = /** @type {NodeListOf<HTMLFormElement>} */($container.querySelectorAll(".list_folder_form"));

        for (let i = 0; i < $forms.length; i++) {
            const $form = $forms[i];
            $form.onsubmit = (e) => {
                e.preventDefault();
                const url = $form.action;
                const csrfmiddlewaretoken = /** @type {HTMLInputElement} */($form.querySelector("input[name=csrfmiddlewaretoken]")).value;
                const $button = /** @type {HTMLButtonElement} */($form.querySelector("button"));
                const paramName = $button.name;
                const value = $button.value;
                const body = new FormData();
                body.append("csrfmiddlewaretoken", csrfmiddlewaretoken);
                body.append(paramName, value);
                fetch(url, { method: 'POST', body }).then(() => {
                    $parentButton.classList.remove("button");
                    $parentButton.classList.add("button_already");
                    $parentButton.textContent = (/** @type {string} */($parentButton.textContent)).replace("+", "✔ ");

                    const $parent = /** @type {HTMLAnchorElement} */($form.parentElement);

                    $parent.removeChild($form);

                    const $addedButton = document.createElement("button");
                    $addedButton.classList.add("button_already");
                    $addedButton.disabled = true;
                    $addedButton.textContent = "Added";
                    $parent.prepend($addedButton);
                });
                return false;
            };
        }
    }

    const $containers = /** @type {NodeListOf<HTMLDivElement>} */(document.querySelectorAll(".list_folder_button_container"));
    for (let i = 0; i < $containers.length; i++) {
        setupButtonContainer($containers[i]);
    }
});
