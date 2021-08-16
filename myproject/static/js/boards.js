$(function () {

  /* Functions */

  var loadForm = function () {
    var btn = $(this);
    $.ajax({
      url: btn.attr("data-url"),
      type: 'get',
      dataType: 'json',
      beforeSend: function () {
        $("#modal-board .modal-content").html("");
        $("#modal-board").modal("show");
      },
      success: function (data) {
        $("#modal-board .modal-content").html(data.html_form);
      }
    });
  };

  var saveForm = function () {
    var form = $(this);
    $.ajax({
      url: form.attr("action"),
      data: form.serialize(),
      type: form.attr("method"),
      dataType: 'json',
      success: function (data) {
        console.log("DATA", data);
        console.log("DATA_HOME", data.html_messages);
        if (data.form_is_valid) {
          $("#board-table tbody").html(data.html_home);
          $("#modal-board").modal("hide");
          // let messages = document.querySelector("ul.messages");
          // let message = "Board updated!"
          // messages.innerHTML = `
          //   <li class=\"{{ message.tags }}\">
          //       ${message}
          //   </li>`;

          $("#message-div").html(data.html_messages);
     //      $('#message-div').html(data).fadeIn('slow');
     // //$('#msg').html("data insert successfully").fadeIn('slow') //also show a success message
     //      $('#message-div').delay(5000).fadeOut('slow');
        }
        else {
          $("#modal-board .modal-content").html(data.html_form);
                    $("#success-message table").html(data.html_home);

        }
      }
    });
    return false;
  };


  /* Binding */

  // Create book
  $(".js-create-board").click(loadForm);
  $("#modal-board").on("submit", ".js-board-create-form", saveForm);

  // Update book

  $("#board-table").on("click", ".js-update-board", loadForm);

  $("#modal-board").on("submit", ".js-board-update-form", saveForm);
  $("#success-message").on("submit", ".js-board-update-form", saveForm);
  // $("#messages").load();

  // Delete book

  $("#board-table").on("click", ".js-delete-board", loadForm);
  $("#modal-board").on("submit", ".js-board-delete-form", saveForm);

});

