$(document).ready(
    $("select[name='equipment']").change(function () {
        // создаем AJAX-вызов
        $.ajax({
            data: {
                    'equipment': $(this).val(),
                    'id': $(this).context.attributes.id.value,
                    },                                              // получаем данные формы
            url: "{% url 'get_ports' %}",
            context: $(this).context.parentElement,
            // если успешно, то
            success: function (response) {
                    console.log(response)
                    console.log('this = ', $(this))

                if (response) {
                    console.log($(this))
                    $(this).html(response);
                }
                else {
                    $('#id_username').removeClass('is-invalid').addClass('is-valid');
                    $('#usernameError').remove();
                }
            },
            // если ошибка, то
            error: function (response) {
                // предупредим об ошибке
                console.log(response.responseJSON.errors)
            }
        });
        return false;
    })
)


function getCookie(name) {
              const value = `; ${document.cookie}`;
              const parts = value.split(`; ${name}=`);
              if (parts.length === 2) {
                const csrfToken = parts.pop().split(';').shift();
    //            console.log(`CSRF Token found: ${csrfToken}`);
                return csrfToken;
              }
              console.log(`CSRF Token not found`);
              return null;
            }
