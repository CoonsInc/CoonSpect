// utils/mdUtils.ts

export const copyToClipboard = (text: string, textarea: HTMLTextAreaElement | null) => {
    if (!navigator.clipboard) {
        if (textarea) {
            textarea.select();
            document.execCommand('copy');
            textarea.setSelectionRange(text.length, text.length);
        }
    } else {
        navigator.clipboard.writeText(text).catch(() => {
            if (textarea) {
                textarea.select();
                document.execCommand('copy');
                textarea.setSelectionRange(text.length, text.length);
            }
        });
    }
};

export const getLineInfo = (text: string, position: number) => {
    const textBeforeCursor = text.substring(0, position);
    const textAfterCursor = text.substring(position);
    const linesBefore = textBeforeCursor.split('\n');
    const linesAfter = textAfterCursor.split('\n');

    const currentLineIndex = linesBefore.length - 1;
    const currentLine = linesBefore[currentLineIndex] + (linesAfter[0] || '');
    const lineStartPosition = position - linesBefore[currentLineIndex].length;
    const lineEndPosition = lineStartPosition + currentLine.length;
    
    return { currentLine, currentLineIndex, lineStartPosition, lineEndPosition };
};

type FormatType = 'bold' | 'italic' | 'list' | 'heading' | 'quote' | 'link';

export const applyFormat = (text: string, start: number, end: number, type: FormatType) => {
    const selectedText = text.substring(start, end);
    let newText = '';
    let newCursorPos = start;

    switch (type) {
        case 'bold': {
            const boldBefore = text.substring(start - 2, start) === '**';
            const boldAfter = text.substring(end, end + 2) === '**';
            
            if (boldBefore && boldAfter) {
                newText = text.substring(0, start - 2) + selectedText + text.substring(end + 2);
                newCursorPos = start - 2;
            } else {
                newText = text.substring(0, start) + `**${selectedText}**` + text.substring(end);
                newCursorPos = start + 2;
            }
            break;
        }
        case 'italic': {
            const italicBefore = text.substring(start - 1, start) === '*';
            const italicAfter = text.substring(end, end + 1) === '*';
            
            if (italicBefore && italicAfter) {
                newText = text.substring(0, start - 1) + selectedText + text.substring(end + 1);
                newCursorPos = start - 1;
            } else {
                newText = text.substring(0, start) + `*${selectedText}*` + text.substring(end);
                newCursorPos = start + 1;
            }
            break;
        }
        case 'list':
        case 'heading':
        case 'quote': {
            const lineInfo = getLineInfo(text, start);
            const prefix = type === 'list' ? '- ' : type === 'heading' ? '## ' : '> ';
            const currentLine = lineInfo.currentLine;
            
            if (currentLine.startsWith(prefix)) {
                const newLine = currentLine.substring(prefix.length);
                newText = text.substring(0, lineInfo.lineStartPosition) + newLine + text.substring(lineInfo.lineEndPosition);
                newCursorPos = lineInfo.lineStartPosition + newLine.length;
            } else {
                const newLine = prefix + currentLine;
                newText = text.substring(0, lineInfo.lineStartPosition) + newLine + text.substring(lineInfo.lineEndPosition);
                newCursorPos = lineInfo.lineStartPosition + newLine.length;
            }
            break;
        }
        case 'link': {
            if (selectedText) {
                const linkRegex = /^\[(.*)\]\((.*)\)$/;
                const match = selectedText.match(linkRegex);
                
                if (match) {
                    const linkText = match[1];
                    newText = text.substring(0, start) + linkText + text.substring(end);
                    newCursorPos = start + linkText.length;
                } else {
                    const formattedText = `[${selectedText}](https://)`;
                    newText = text.substring(0, start) + formattedText + text.substring(end);
                    newCursorPos = start + 1 + selectedText.length + 2;
                }
            } else {
                const formattedText = '[текст ссылки](https://)';
                newText = text.substring(0, start) + formattedText + text.substring(end);
                newCursorPos = start + 13;
            }
            break;
        }
    }

    return { newText, newCursorPos };
};

export const parseMarkdownToHtml = (text: string) => {
    if (!text.trim()) return '';

    return text
        .split('\n')
        .map(line => {
            if (line.startsWith('## ')) {
                return `<h3 class="text-xl font-bold mt-4 mb-2 text-[var(--color-text-primary)]">${line.slice(3)}</h3>`;
            }
            if (line.startsWith('> ')) {
                return `<blockquote class="border-l-4 border-[var(--color-text-purple)] pl-4 my-2 text-[var(--color-text-secondary)] italic">${line.slice(2)}</blockquote>`;
            }
            if (line.startsWith('- ')) {
                return `<li class="ml-4 text-[var(--color-text-primary)] mb-1 list-disc">${line.slice(2)}</li>`;
            }
            if (line.trim() === '') {
                return '<br>';
            }

            let processedLine = line
                .replace(/\*\*(.*?)\*\*/g, '<strong class="font-bold text-[var(--color-text-primary)]">$1</strong>')
                .replace(/\*(.*?)\*/g, '<em class="italic text-[var(--color-text-secondary)]">$1</em>')
                .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" class="text-[var(--color-text-purple)] hover:opacity-80 underline" target="_blank" rel="noopener noreferrer">$1</a>');
            
            return `<p class="mb-3 text-[var(--color-text-primary)] leading-relaxed">${processedLine}</p>`;
        })
        .join('');
};
