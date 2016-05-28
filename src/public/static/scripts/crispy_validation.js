/**
 * Created by Nikita on 28.04.2016.
 */
function crispy_init() {
    var example_form = $;

    $.ajax({
        url: "{% url 'save_example_form' %}",
        type: "POST",
        data: $(example_form).serialize(),
        success: function (data) {
            if (!(data['success'])) {
                // Here we replace the form, for the
                $(example_form).replaceWith(data['form_html']);
            }
            else {
                // Here you can show the user a success message or do whatever you need
                $(example_form).find('.success-message').show();
            }
        },
        error: function () {
            $(example_form).find('.error-message').show()
        }
    });
}