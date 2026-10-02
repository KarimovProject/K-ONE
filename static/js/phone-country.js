/* Wraps every <input type="tel"> with a country/dial-code <select>; picking
 * a country prepends its "+code" to the phone field (default: O'zbekiston). */
(function () {
  "use strict";

  // [ISO2, dial code, Uzbek name]
  var COUNTRIES = [
    ["UZ", "998", "O'zbekiston"],
    ["AF", "93", "Afg'oniston"],
    ["AL", "355", "Albaniya"],
    ["DZ", "213", "Jazoir"],
    ["AD", "376", "Andorra"],
    ["AO", "244", "Angola"],
    ["AG", "1268", "Antigua va Barbuda"],
    ["AR", "54", "Argentina"],
    ["AM", "374", "Armaniston"],
    ["AU", "61", "Avstraliya"],
    ["AT", "43", "Avstriya"],
    ["AZ", "994", "Ozarbayjon"],
    ["BS", "1242", "Bagama orollari"],
    ["BH", "973", "Bahrayn"],
    ["BD", "880", "Bangladesh"],
    ["BB", "1246", "Barbados"],
    ["BY", "375", "Belarus"],
    ["BE", "32", "Belgiya"],
    ["BZ", "501", "Beliz"],
    ["BJ", "229", "Benin"],
    ["BT", "975", "Butan"],
    ["BO", "591", "Boliviya"],
    ["BA", "387", "Bosniya va Gertsegovina"],
    ["BW", "267", "Botsvana"],
    ["BR", "55", "Braziliya"],
    ["BN", "673", "Bruney"],
    ["BG", "359", "Bolgariya"],
    ["BF", "226", "Burkina-Faso"],
    ["BI", "257", "Burundi"],
    ["KH", "855", "Kambodja"],
    ["CM", "237", "Kamerun"],
    ["CA", "1", "Kanada"],
    ["CV", "238", "Kabo-Verde"],
    ["CF", "236", "Markaziy Afrika Respublikasi"],
    ["TD", "235", "Chad"],
    ["CL", "56", "Chili"],
    ["CN", "86", "Xitoy"],
    ["CO", "57", "Kolumbiya"],
    ["KM", "269", "Komor orollari"],
    ["CG", "242", "Kongo"],
    ["CD", "243", "Kongo Demokratik Respublikasi"],
    ["CR", "506", "Kosta-Rika"],
    ["CI", "225", "Kot-d'Ivuar"],
    ["HR", "385", "Xorvatiya"],
    ["CU", "53", "Kuba"],
    ["CY", "357", "Kipr"],
    ["CZ", "420", "Chexiya"],
    ["DK", "45", "Daniya"],
    ["DJ", "253", "Jibuti"],
    ["DM", "1767", "Dominika"],
    ["DO", "1809", "Dominikan Respublikasi"],
    ["EC", "593", "Ekvador"],
    ["EG", "20", "Misr"],
    ["SV", "503", "Salvador"],
    ["GQ", "240", "Ekvatorial Gvineya"],
    ["ER", "291", "Eritreya"],
    ["EE", "372", "Estoniya"],
    ["SZ", "268", "Esvatini"],
    ["ET", "251", "Efiopiya"],
    ["FJ", "679", "Fiji"],
    ["FI", "358", "Finlyandiya"],
    ["FR", "33", "Fransiya"],
    ["GA", "241", "Gabon"],
    ["GM", "220", "Gambiya"],
    ["GE", "995", "Gruziya"],
    ["DE", "49", "Germaniya"],
    ["GH", "233", "Gana"],
    ["GR", "30", "Gretsiya"],
    ["GD", "1473", "Grenada"],
    ["GT", "502", "Gvatemala"],
    ["GN", "224", "Gvineya"],
    ["GW", "245", "Gvineya-Bisau"],
    ["GY", "592", "Gayana"],
    ["HT", "509", "Gaiti"],
    ["HN", "504", "Gonduras"],
    ["HK", "852", "Gonkong"],
    ["HU", "36", "Vengriya"],
    ["IS", "354", "Islandiya"],
    ["IN", "91", "Hindiston"],
    ["ID", "62", "Indoneziya"],
    ["IR", "98", "Eron"],
    ["IQ", "964", "Iroq"],
    ["IE", "353", "Irlandiya"],
    ["IL", "972", "Isroil"],
    ["IT", "39", "Italiya"],
    ["JM", "1876", "Yamayka"],
    ["JP", "81", "Yaponiya"],
    ["JO", "962", "Iordaniya"],
    ["KZ", "7", "Qozog'iston"],
    ["KE", "254", "Keniya"],
    ["KI", "686", "Kiribati"],
    ["KP", "850", "Shimoliy Koreya"],
    ["KR", "82", "Janubiy Koreya"],
    ["XK", "383", "Kosovo"],
    ["KW", "965", "Kuvayt"],
    ["KG", "996", "Qirg'iziston"],
    ["LA", "856", "Laos"],
    ["LV", "371", "Latviya"],
    ["LB", "961", "Livan"],
    ["LS", "266", "Lesoto"],
    ["LR", "231", "Liberiya"],
    ["LY", "218", "Liviya"],
    ["LI", "423", "Lixtenshteyn"],
    ["LT", "370", "Litva"],
    ["LU", "352", "Lyuksemburg"],
    ["MO", "853", "Makao"],
    ["MG", "261", "Madagaskar"],
    ["MW", "265", "Malavi"],
    ["MY", "60", "Malayziya"],
    ["MV", "960", "Maldiv orollari"],
    ["ML", "223", "Mali"],
    ["MT", "356", "Malta"],
    ["MH", "692", "Marshall orollari"],
    ["MR", "222", "Mavritaniya"],
    ["MU", "230", "Mavrikiy"],
    ["MX", "52", "Meksika"],
    ["FM", "691", "Mikroneziya"],
    ["MD", "373", "Moldova"],
    ["MC", "377", "Monako"],
    ["MN", "976", "Mongoliya"],
    ["ME", "382", "Chernogoriya"],
    ["MA", "212", "Marokash"],
    ["MZ", "258", "Mozambik"],
    ["MM", "95", "Myanma"],
    ["NA", "264", "Namibiya"],
    ["NR", "674", "Nauru"],
    ["NP", "977", "Nepal"],
    ["NL", "31", "Niderlandiya"],
    ["NZ", "64", "Yangi Zelandiya"],
    ["NI", "505", "Nikaragua"],
    ["NE", "227", "Niger"],
    ["NG", "234", "Nigeriya"],
    ["MK", "389", "Shimoliy Makedoniya"],
    ["NO", "47", "Norvegiya"],
    ["OM", "968", "Ummon"],
    ["PK", "92", "Pokiston"],
    ["PW", "680", "Palau"],
    ["PS", "970", "Falastin"],
    ["PA", "507", "Panama"],
    ["PG", "675", "Papua — Yangi Gvineya"],
    ["PY", "595", "Paragvay"],
    ["PE", "51", "Peru"],
    ["PH", "63", "Filippin"],
    ["PL", "48", "Polsha"],
    ["PT", "351", "Portugaliya"],
    ["QA", "974", "Qatar"],
    ["RO", "40", "Ruminiya"],
    ["RU", "7", "Rossiya"],
    ["RW", "250", "Ruanda"],
    ["KN", "1869", "Sent-Kits va Nevis"],
    ["LC", "1758", "Sent-Lyusiya"],
    ["VC", "1784", "Sent-Vinsent va Grenadin"],
    ["WS", "685", "Samoa"],
    ["SM", "378", "San-Marino"],
    ["ST", "239", "San-Tome va Prinsipi"],
    ["SA", "966", "Saudiya Arabistoni"],
    ["SN", "221", "Senegal"],
    ["RS", "381", "Serbiya"],
    ["SC", "248", "Seyshel orollari"],
    ["SL", "232", "Serra-Leone"],
    ["SG", "65", "Singapur"],
    ["SK", "421", "Slovakiya"],
    ["SI", "386", "Sloveniya"],
    ["SB", "677", "Solomon orollari"],
    ["SO", "252", "Somali"],
    ["ZA", "27", "Janubiy Afrika Respublikasi"],
    ["SS", "211", "Janubiy Sudan"],
    ["ES", "34", "Ispaniya"],
    ["LK", "94", "Shri-Lanka"],
    ["SD", "249", "Sudan"],
    ["SR", "597", "Surinam"],
    ["SE", "46", "Shvetsiya"],
    ["CH", "41", "Shveytsariya"],
    ["SY", "963", "Suriya"],
    ["TW", "886", "Tayvan"],
    ["TJ", "992", "Tojikiston"],
    ["TZ", "255", "Tanzaniya"],
    ["TH", "66", "Tayland"],
    ["TL", "670", "Sharqiy Timor"],
    ["TG", "228", "Togo"],
    ["TO", "676", "Tonga"],
    ["TT", "1868", "Trinidad va Tobago"],
    ["TN", "216", "Tunis"],
    ["TR", "90", "Turkiya"],
    ["TM", "993", "Turkmaniston"],
    ["TV", "688", "Tuvalu"],
    ["UG", "256", "Uganda"],
    ["UA", "380", "Ukraina"],
    ["AE", "971", "BAA (Birlashgan Arab Amirliklari)"],
    ["GB", "44", "Buyuk Britaniya"],
    ["US", "1", "AQSH"],
    ["UY", "598", "Urugvay"],
    ["VU", "678", "Vanuatu"],
    ["VA", "379", "Vatikan"],
    ["VE", "58", "Venesuela"],
    ["VN", "84", "Vyetnam"],
    ["YE", "967", "Yaman"],
    ["ZM", "260", "Zambiya"],
    ["ZW", "263", "Zimbabve"],
  ];

  // Longest dial code first, so "+998" isn't mis-matched as "+9".
  var BY_DIAL_LENGTH = COUNTRIES.slice().sort(function (a, b) {
    return b[1].length - a[1].length;
  });

  function detectCountry(value) {
    var match = /^\+?(\d+)/.exec((value || "").trim());
    if (!match) return null;
    var digits = match[1];
    for (var i = 0; i < BY_DIAL_LENGTH.length; i++) {
      if (digits.indexOf(BY_DIAL_LENGTH[i][1]) === 0) return BY_DIAL_LENGTH[i];
    }
    return null;
  }

  function flagEmoji(iso2) {
    var codePoints = iso2
      .toUpperCase()
      .split("")
      .map(function (c) {
        return 127397 + c.charCodeAt(0);
      });
    return String.fromCodePoint.apply(String, codePoints);
  }

  function buildSelect(selected) {
    var select = document.createElement("select");
    select.className = "phone-country-select";
    select.setAttribute("aria-label", "Davlat kodi");
    COUNTRIES.forEach(function (country) {
      var option = document.createElement("option");
      option.value = country[1];
      option.dataset.iso = country[0];
      option.textContent = flagEmoji(country[0]) + " +" + country[1];
      option.title = country[2] + " (+" + country[1] + ")";
      if (selected && selected[0] === country[0]) option.selected = true;
      select.appendChild(option);
    });
    select.title = select.options[select.selectedIndex]
      ? select.options[select.selectedIndex].title
      : "";
    select.addEventListener("change", function () {
      select.title = select.options[select.selectedIndex].title;
    });
    return select;
  }

  function wrap(input) {
    if (input.dataset.phoneWrapped) return;
    input.dataset.phoneWrapped = "1";

    var current = detectCountry(input.value) || COUNTRIES[0];
    var select = buildSelect(current);

    var group = document.createElement("div");
    group.className = "phone-input-group";
    input.parentNode.insertBefore(group, input);
    group.appendChild(select);
    group.appendChild(input);

    if (!detectCountry(input.value)) {
      var rest = input.value.replace(/^\+?\d*\s*/, "");
      input.value = "+" + current[1] + (rest ? " " + rest : "");
    }

    select.addEventListener("change", function () {
      var existing = detectCountry(input.value);
      var rest = existing
        ? input.value.slice(input.value.indexOf(existing[1]) + existing[1].length).replace(/^[\s-]*/, "")
        : input.value.replace(/^\+?\d*\s*/, "");
      input.value = "+" + select.value + (rest ? " " + rest : "");
      input.focus();
    });
  }

  function init() {
    document.querySelectorAll('input[type="tel"]').forEach(wrap);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
