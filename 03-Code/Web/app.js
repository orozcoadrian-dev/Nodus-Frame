const tokenDetails = {
  turn: { text: "Delimita cada intervención y hace explícito quién está hablando.", close: "<turn|>" },
  think: { text: "Activa el canal interno. Su contenido debe permanecer oculto al usuario final.", close: "<|channel>thought ... <channel|>" },
  call: { text: "Pausa la generación para que tu aplicación ejecute una función registrada.", close: "<tool_call|>" },
  response: { text: "Reinyecta el resultado de la herramienta para que el modelo pueda continuar.", close: "<tool_response|>" },
  media: { text: "Reserva una posición para embeddings de imagen o audio dentro del turno.", close: "<|audio|>" }
};

const detail = document.querySelector("#token-detail");
document.querySelectorAll(".token-card").forEach((card) => {
  card.addEventListener("click", () => {
    document.querySelectorAll(".token-card").forEach((item) => item.classList.remove("active"));
    card.classList.add("active");
    const selected = tokenDetails[card.dataset.token];
    detail.querySelector("p").textContent = selected.text;
    detail.querySelector("code").textContent = selected.close;
  });
});

let selectedRole = "user";
const input = document.querySelector("#prompt-input");
const output = document.querySelector("#prompt-output");
const count = document.querySelector("#char-count");

function escapeHtml(value) {
  return value.replace(/[&<>]/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[character]));
}

function updatePrompt() {
  const content = input.value || "...";
  const raw = `<|turn>${selectedRole}\n${content}<turn|>`;
  output.innerHTML = raw
    .split(/(<\|turn>|<turn\|>)/g)
    .map((part) => part.startsWith("<|") || part === "<turn|>" ? `<span class="syntax-tag">${escapeHtml(part)}</span>` : `<span class="syntax-${part === selectedRole ? "role" : "text"}">${escapeHtml(part)}</span>`)
    .join("");
  count.textContent = `${input.value.length} caracteres`;
}

document.querySelectorAll(".segmented-button").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".segmented-button").forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    selectedRole = button.dataset.role;
    updatePrompt();
  });
});
input.addEventListener("input", updatePrompt);
document.querySelector("#reset-prompt").addEventListener("click", () => {
  input.value = "Describe el ciclo de una herramienta en una frase.";
  selectedRole = "user";
  document.querySelectorAll(".segmented-button").forEach((item) => item.classList.toggle("active", item.dataset.role === "user"));
  updatePrompt();
});
document.querySelector("#copy-prompt").addEventListener("click", async (event) => {
  await navigator.clipboard.writeText(`<|turn>${selectedRole}\n${input.value}<turn|>`);
  const button = event.currentTarget;
  const original = button.innerHTML;
  button.innerHTML = "Copiado ✓";
  setTimeout(() => { button.innerHTML = original; }, 1300);
});

document.querySelector("#run-tool").addEventListener("click", (event) => {
  const callLine = document.querySelector("#tool-call-line");
  const resultLine = document.querySelector("#tool-result-line");
  const button = event.currentTarget;
  callLine.innerHTML = '<span class="prompt-caret">›</span> call:get_weather{city:<|"|>Madrid<|"|>}';
  resultLine.classList.remove("hidden");
  button.textContent = "Simulación completada ✓";
  setTimeout(() => { button.innerHTML = "Ejecutar de nuevo <span>→</span>"; }, 1800);
});

updatePrompt();