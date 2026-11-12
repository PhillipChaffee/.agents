export function typographyViolations(text, file) {
	const violations = [];
	const lines = text.split("\n");
	const frontmatterEndLine = text.startsWith("---\n")
		? lines.findIndex((line, index) => index > 0 && line.trim() === "---")
		: -1;
	let inFence = false;
	lines.forEach((line, index) => {
		const trimmed = line.trim();
		if (index <= frontmatterEndLine) return;
		if (trimmed.startsWith("```") || trimmed.startsWith("~~~")) {
			inFence = !inFence;
			return;
		}
		if (/[\u2013\u2014]/.test(line)) {
			violations.push(`${file}:${index + 1}: dash character ${trimmed}`);
		}
		if (inFence || trimmed === "" || trimmed.startsWith("|") || trimmed.startsWith("#")) return;
		const prose = line
			.replace(/`[^`]*`/g, "")
			.replace(/https?:\/\/\S+/g, "")
			.replace(/\([^)]*\)/g, "");
		if (!prose.includes(":")) return;
		if (prose.trimEnd().endsWith(":")) return;
		violations.push(`${file}:${index + 1}: mid-sentence colon ${trimmed}`);
	});
	return violations;
}
