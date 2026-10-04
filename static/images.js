// Freely licensed stock photos (Wikimedia Commons / Flickr via Openverse).
// If a photo cannot load, the app shows a coloured illustrated placeholder.
// To keep photos offline: save them into static/img/<key>.jpg — local files are tried first.
window.IMAGES = {
  hero:        { url: "https://upload.wikimedia.org/wikipedia/commons/thumb/b/ba/Soyabean_Harvsting_in_Rural_Maharashtra%2C_India.jpg/960px-Soyabean_Harvsting_in_Rural_Maharashtra%2C_India.jpg", title: "Soyabean Harvesting in Rural Maharashtra, India", lic: "CC BY-SA 4.0", src: "Wikimedia Commons", emoji: "👨‍🌾", tint: "#2f6b3a" },
  dry:         { url: "https://live.staticflickr.com/4147/5096063653_ef53e068ec_b.jpg", title: "Zemlja_01 (cracked earth)", lic: "CC BY 2.0", src: "Flickr", emoji: "🏜️", tint: "#b4743a" },
  clouds:      { url: "https://live.staticflickr.com/3756/9421742217_bfefed0982_b.jpg", title: "Down on the farm...", lic: "CC BY 2.0", src: "Flickr", emoji: "🌦️", tint: "#4a7bab" },
  farmer:      { url: "https://live.staticflickr.com/3384/3573950261_53e5aca5f2_b.jpg", title: "Indian farmer", lic: "CC BY 2.0", src: "Flickr", emoji: "🧑‍🌾", tint: "#6b8e23" },
  tur:         { url: "https://upload.wikimedia.org/wikipedia/commons/thumb/8/83/Pigeon_Pea_field_in_Andhra_Pradesh_%2813053%29.jpg/960px-Pigeon_Pea_field_in_Andhra_Pradesh_%2813053%29.jpg", title: "Pigeon Pea field in Andhra Pradesh", lic: "CC BY-SA 3.0", src: "Wikimedia Commons", emoji: "🌿", tint: "#5b8c32" },
  soy_tur:     { url: "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/Pigeon_Pea_field_in_Andhra_Pradesh_%2833035%29.jpg/960px-Pigeon_Pea_field_in_Andhra_Pradesh_%2833035%29.jpg", title: "Pigeon Pea field in Andhra Pradesh", lic: "CC BY-SA 3.0", src: "Wikimedia Commons", emoji: "🌱", tint: "#4f8a3c" },
  soybean:     { url: "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fc/Soyabean_field.jpg/960px-Soyabean_field.jpg", title: "Soyabean field", lic: "CC BY-SA 3.0", src: "Wikimedia Commons", emoji: "🫘", tint: "#7a9a2e" },
  cotton:      { url: "https://live.staticflickr.com/3438/3932158214_13b108d26c_b.jpg", title: "Champs de coton / Agriculteur", lic: "CC BY 2.0", src: "Flickr", emoji: "☁️", tint: "#8a9bb0" },
  jowar:       { url: "https://upload.wikimedia.org/wikipedia/commons/thumb/8/84/Sorghum_Field_El_Salvador_2011.jpg/960px-Sorghum_Field_El_Salvador_2011.jpg", title: "Sorghum Field El Salvador 2011", lic: "CC0", src: "Wikimedia Commons", emoji: "🌾", tint: "#a3772c" },
  bajra:       { url: "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f0/Grain_millet%2C_early_grain_fill%2C_Tifton%2C_7-3-02.jpg/960px-Grain_millet%2C_early_grain_fill%2C_Tifton%2C_7-3-02.jpg", title: "Grain millet, early grain fill, Tifton", lic: "Public domain", src: "Wikimedia Commons", emoji: "🌾", tint: "#9a8a3a" },
  moong:       { url: "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/Green_Gram_field.jpg/960px-Green_Gram_field.jpg", title: "Green Gram field", lic: "CC BY-SA 4.0", src: "Wikimedia Commons", emoji: "🟢", tint: "#3f8f4f" },
  chickpea:    { url: "https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Chickpea_field.jpg/960px-Chickpea_field.jpg", title: "Chickpea field", lic: "CC BY 2.5", src: "Wikimedia Commons", emoji: "🧆", tint: "#8c9a3c" },
  safflower:   { url: "https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Yamagata_safflower_field.jpg/960px-Yamagata_safflower_field.jpg", title: "Yamagata safflower field", lic: "CC0", src: "Wikimedia Commons", emoji: "🌼", tint: "#e0952b" },
  wheat:       { url: "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Wheat_fields_India.jpg/960px-Wheat_fields_India.jpg", title: "Wheat fields India", lic: "CC BY-SA 4.0", src: "Wikimedia Commons", emoji: "🌾", tint: "#c49a35" },
  paddy:       { url: "https://upload.wikimedia.org/wikipedia/commons/thumb/b/be/Paddy_field_India.jpg/960px-Paddy_field_India.jpg", title: "Paddy field India", lic: "CC BY-SA 3.0", src: "Wikimedia Commons", emoji: "🍚", tint: "#4c9a52" },
  soil_black:  { url: "https://live.staticflickr.com/2372/2259630259_88e904028e_b.jpg", title: "Black soil", lic: "CC BY-SA 2.0", src: "Flickr", emoji: "🟫", tint: "#3b2f2a" },
  soil_medium: { url: "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b9/A_red_soil_crop_field.JPG/960px-A_red_soil_crop_field.JPG", title: "A red soil crop field", lic: "CC BY-SA 3.0", src: "Wikimedia Commons", emoji: "🟤", tint: "#8b4a2b" },
  soil_light:  { url: "https://upload.wikimedia.org/wikipedia/commons/thumb/9/93/Dry_forest_on_sandy_soils.jpg/960px-Dry_forest_on_sandy_soils.jpg", title: "Dry forest on sandy soils", lic: "CC BY-SA 4.0", src: "Wikimedia Commons", emoji: "🏖️", tint: "#c9a46a" },
  water_rain:  { url: "https://live.staticflickr.com/2716/5831565710_f2e0de574a_b.jpg", title: "And the rain starts", lic: "CC BY 2.0", src: "Flickr", emoji: "🌧️", tint: "#4a6f9b" },
  water_well:  { url: "https://live.staticflickr.com/3562/3366403351_c714cca771.jpg", title: "water, hodko banni", lic: "CC BY 2.0", src: "Flickr", emoji: "🪣", tint: "#5b7f8f" },
  water_canal: { url: "https://live.staticflickr.com/2518/3756928925_4339eaf8d8_b.jpg", title: "The Famous Kannadigan Irrigation Canal", lic: "CC BY 2.0", src: "Flickr", emoji: "🏞️", tint: "#2f7f9b" },
};
window.IMAGES.season_kharif = window.IMAGES.clouds;
window.IMAGES.season_rabi = window.IMAGES.wheat;
