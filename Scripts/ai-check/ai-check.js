const targetNode = (typeof $environment !== "undefined" && $environment.executeNode) ?$environment.executeNode : undefined;
function req(url) {
    return new Promise(resolve => {
        $task.fetch({ url: url, method: "GET", headers: { "User-Agent": "Mozilla/5.0" }, node: targetNode, timeout: 5000 })
            .then(resp => resolve({ status: resp.statusCode }), () => resolve({ status: 0 }));
    });
}
async function checkAI() {
    const [gpt, claude, gemini, copilot] = await Promise.all([
        req("https://chatgpt.com/"), req("https://claude.ai/login"), req("https://gemini.google.com/"), req("https://copilot.microsoft.com/")
    ]);
    const lines = [
        `🧠 ChatGPT: ${gpt.status === 200 ? "🟢 完美支持" : "🔴 受限"}`,
        `🎭 Claude: ${claude.status === 200 ? "🟢 完美支持" : "🔴 地区受限"}`,
        `✨ Gemini: ${(gemini.status === 200 || gemini.status === 302) ? "🟢 完美支持" : "🔴 受限"}`,
        `💻 Copilot: ${copilot.status === 200 ? "🟢 正常可用" : "🔴 受限"}`
    ];
    $done({ title: "🤖 AI 智能助手诊断", message: lines.join("\n"), content: lines.join("\n") });
}
checkAI();
