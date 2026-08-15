const languageSelector = document.querySelector("[data-language-selector]");
const languageForm = document.querySelector("[data-language-form]");
const languageSubmit = document.querySelector("[data-language-submit]");

if (languageSelector && languageForm) {
  const navigateToSelectedLanguage = () => {
    const target = new URL(window.location.href);
    target.searchParams.set("lang", languageSelector.value);
    window.location.assign(target.toString());
  };

  languageSelector.addEventListener("change", navigateToSelectedLanguage);
  languageForm.addEventListener("submit", (event) => {
    event.preventDefault();
    navigateToSelectedLanguage();
  });

  if (languageSubmit) {
    languageSubmit.hidden = true;
  }
}
