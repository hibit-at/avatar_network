// @ts-check

document.addEventListener("DOMContentLoaded", () => {
    const $forms = /** @type {NodeListOf<HTMLFormElement>} */(document.querySelectorAll(".list_folder_form"));
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
            fetch(url, { method: 'POST', body }).then(() => window.location.reload());
            return false;
        };
    }
});
