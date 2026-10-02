/* Wires intl-tel-input (static/vendor/intl-tel-input/) onto every
 * input[type="tel"] — the self-written flag/dial-code widget was replaced
 * with this well-known library for a standard, polished look. */
(function () {
  "use strict";

  if (typeof window.intlTelInput !== "function") return;

  var COUNTRY_ORDER = ["uz", "kz", "kg", "tj", "tm", "ru", "az", "by", "ua", "tr"];

  function initPhoneField(input) {
    if (input.dataset.itiInitialized) return;
    input.dataset.itiInitialized = "1";

    var iti = window.intlTelInput(input, {
      initialCountry: "uz",
      countryOrder: COUNTRY_ORDER,
      separateDialCode: true,
      nationalMode: false,
      strictMode: true,
    });

    var form = input.closest("form");
    if (form) {
      form.addEventListener("submit", function () {
        var full = iti.getNumber && iti.getNumber();
        if (full) input.value = full;
      });
    }
  }

  function init() {
    document.querySelectorAll('input[type="tel"]').forEach(initPhoneField);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
