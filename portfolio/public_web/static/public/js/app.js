const languageSelector = document.querySelector("[data-language-selector]");
const languageStatus = document.querySelector("[data-language-status]");

if (languageSelector && languageStatus) {
  languageSelector.addEventListener("change", (event) => {
    const selectedLanguage = event.target.value;
    document.documentElement.lang = selectedLanguage;
    languageStatus.textContent = `Language preference placeholder: ${selectedLanguage}`;
  });
}
