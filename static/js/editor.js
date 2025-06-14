require.config({ paths: { vs: 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.21.2/min/vs' } });
require(['vs/editor/editor.main'], function () {
  const editor = monaco.editor.create(document.getElementById('editor'), {
    value: "# class BossAI:\n#     def __init__(self):\n#         pass\n",
    language: 'python',
    theme: 'vs-dark',
    automaticLayout: true
  });

  document.querySelector("form").addEventListener("submit", function (e) {
    const captcha = document.getElementById("captcha").value;
    if (captcha.trim() !== "5") {
      alert("Captcha incorrect.");
      e.preventDefault();
      return;
    }
    document.getElementById("code").value = editor.getValue();
    document.getElementById("confirmation").style.display = "block";
  });

  const challengeSelect = document.getElementById("challenge");
  const instructionsBox = document.getElementById("instructions");

  challengeSelect.addEventListener("change", () => {
    const selected = challengeSelect.value;
    let message = "";
    switch (selected) {
      case "boss_ai":
        message = "🎯 Crée une classe 'BossAI' qui change de stratégie selon la vie restante.";
        break;
      case "wave_system":
        message = "🎯 Implémente un système de vagues d'ennemis avec difficulté progressive.";
        break;
      case "pickup_logic":
        message = "🎯 Crée une logique de bonus (soins, munitions) avec gestion de cooldown.";
        break;
      default:
        message = "🔍 Les instructions du défi apparaîtront ici...";
    }
    instructionsBox.innerText = message;
  });
});
