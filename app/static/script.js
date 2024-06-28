document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".edit-button").forEach((button) => {
    button.addEventListener("click", function () {
      var id = this.dataset.id;
      openModifyForm(id);
    });
  });
  document.querySelectorAll(".delete-button").forEach((button) => {
    button.addEventListener("click", function () {
      var id = this.dataset.id;
      window.location.href = `user/delete/${id}`;
    });
  });
});

function openModifyForm(id) {
  container_form = document.querySelector(".container-form");
  form = document.querySelector(".form-action");
  submit_button = document.querySelector("#submit-button");
  form.action = "user/update/" + id;
  submit_button.setAttribute("value", "Update");
  container_form.style.visibility = "visible";
}

function openAddForm() {
  form = document.querySelector(".form-action");
  submit_button = document.querySelector("#submit-button");
  form.action = "user/add";
  submit_button.setAttribute("value", "Add");
  document.querySelector(".container-form").style.visibility = "visible";
}

function closeForm() {
  document.querySelector(".container-form").style.visibility = "hidden";
}
