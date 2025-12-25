export const parseRichText = (text) => {
    // Splits text into an array of tokens: { text: "string", style: "normal" | "bold" | "danger" | "insight" }
    // Supports: *text* (bold), [danger]text[/danger], [insight]text[/insight]

    if (!text) return [];

    const tokens = [];
    let buffer = text;

    // Regex for tags
    // 1. [danger]...[/danger]
    // 2. [insight]...[/insight]
    // 3. *...*

    // We will simply regex for the first occurrence of ANY tag, split, push prefix, push tag, repeat.
    // Order matters? Not really if we just find the earliest match.

    while (buffer.length > 0) {
        // Find earliest tag
        const dangerMatch = buffer.match(/\[danger\](.*?)\[\/danger\]/);
        const insightMatch = buffer.match(/\[insight\](.*?)\[\/insight\]/);
        const boldMatch = buffer.match(/\*(.*?)\*/);

        let bestMatch = null;
        let type = 'normal';
        let matchIndex = Infinity;

        if (dangerMatch && dangerMatch.index < matchIndex) {
            matchIndex = dangerMatch.index;
            bestMatch = dangerMatch;
            type = 'danger';
        }
        if (insightMatch && insightMatch.index < matchIndex) {
            matchIndex = insightMatch.index;
            bestMatch = insightMatch;
            type = 'insight';
        }
        if (boldMatch && boldMatch.index < matchIndex) {
            matchIndex = boldMatch.index;
            bestMatch = boldMatch;
            type = 'bold';
        }

        if (!bestMatch) {
            // No more tags
            tokens.push({ text: buffer, style: 'normal' });
            break;
        }

        // Push text before tag
        if (matchIndex > 0) {
            tokens.push({ text: buffer.slice(0, matchIndex), style: 'normal' });
        }

        // Push tag content
        tokens.push({ text: bestMatch[1], style: type });

        // Advance buffer (match[0] is the full tag string)
        buffer = buffer.slice(matchIndex + bestMatch[0].length);
    }

    return tokens;
};
