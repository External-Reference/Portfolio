// Selezioni di progetti con un link a parte.
// Ogni selezione si apre con index.html?sel=NOME (oppure con la sua pagina, es. expo-exhibition.html).
// "cover" (facoltativo): la foto di copertina, come progetto#numero-foto.
// "home" (facoltativo): le foto che ruotano nella home della selezione (cartella home/NOME), come in home.js.
// "projects": i progetti nell'ordine voluto, scritti come sezione/nome-cartella-senza-numero.
window.ERSEL = {
  "expo-exhibition": {
    "title": "Expo & Exhibition",
    "home": [
      { "img": "home/expo-exhibition/01.webp", "go": "interior/spanish-pavilion-dubai-expo", "title": "Spanish Pavilion, Dubai Expo", "section": "Expo & Pavilions", "place": "Dubai  2021" },
      { "img": "home/expo-exhibition/02.webp", "go": "interior/spanish-pavilion-yeosu-expo", "title": "Spanish Pavilion, Yeosu Expo", "section": "Expo & Pavilions", "place": "Yeosu  2012" },
      { "img": "home/expo-exhibition/03.webp", "go": "interior/european-union-pavilion", "title": "European Union Pavilion", "section": "Expo & Pavilions", "place": "Guadalajara  2023" },
      { "img": "home/expo-exhibition/04.webp", "go": "interior/yota-pavilion-ii", "title": "Yota Pavilion II", "section": "Expo & Pavilions", "place": "Barcelona  2014" }
    ],
    "projects": [
      "interior/spanish-pavilion-dubai-expo",
      "interior/expo-2020-dubai-menasa-emirati-design-platform",
      "interior/spanish-pavilion-yeosu-expo",
      "interior/spanish-pavilion-expo-2027-belgrade",
      "interior/spanish-pavilion-expo-osaka-2025",
      "interior/european-union-pavilion",
      "interior/bershka-x-lollapalooza",
      "interior/braga-fc-museum",
      "interior/liga-portugal",
      "interior/real-madrid-museum",
      "interior/shenzhen-science-museum-main-installation",
      "interior/earlier-mona-lisa-exhibition",
      "interior/yota-pavilion-ii",
      "interior/expo-2020-dubai-peru-pavilion-exhibition",
      "interior/expo-2020-dubai-india-pavilion-exhibition",
      "urban/jeddah-fashion-island",
      "urban/jeddah-formula-1",
      "urban/waves-festival",
      "urban/street-waves"
    ]
  }
};
