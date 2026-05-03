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

type FormatType = 'bold' | 'italic' | 'list' | 'heading' | 'quote' | 'link' | 'divider';

export const applyFormat = (text: string, start: number, end: number, type: FormatType) => {
    const selectedText = text.substring(start, end);
    let newText = '';
    let newCursorPos = start;

    switch (type) {
        case 'bold': {
            const isWrappedInside = selectedText.startsWith('**') && selectedText.endsWith('**') && selectedText.length >= 4;
            const isWrappedOutside = text.substring(start - 2, start) === '**' && text.substring(end, end + 2) === '**';

            if (isWrappedInside) {
                newText = text.substring(0, start) + selectedText.substring(2, selectedText.length - 2) + text.substring(end);
                newCursorPos = end - 4;
            } else if (isWrappedOutside) {
                newText = text.substring(0, start - 2) + selectedText + text.substring(end + 2);
                newCursorPos = start - 2;
            } else {
                const blockMatch = selectedText.match(/^(\s*(?:#{1,4}\s+|> \s*|-\s+))(.*)$/);
                if (blockMatch) {
                    const prefix = blockMatch[1];
                    const actualText = blockMatch[2];
                    newText = text.substring(0, start) + prefix + `**${actualText}**` + text.substring(end);
                    newCursorPos = start + prefix.length + 2;
                } else {
                    newText = text.substring(0, start) + `**${selectedText}**` + text.substring(end);
                    newCursorPos = start + 2;
                }
            }
            break;
        }
        case 'italic': {
            const isWrappedInside = selectedText.startsWith('*') && selectedText.endsWith('*') && selectedText.length >= 2 && !selectedText.startsWith('**');
            const isWrappedOutside = text.substring(start - 1, start) === '*' && text.substring(end, end + 1) === '*' && text.substring(start - 2, start) !== '**';
            
            if (isWrappedInside) {
                newText = text.substring(0, start) + selectedText.substring(1, selectedText.length - 1) + text.substring(end);
                newCursorPos = end - 2;
            } else if (isWrappedOutside) {
                newText = text.substring(0, start - 1) + selectedText + text.substring(end + 1);
                newCursorPos = start - 1;
            } else {
                const blockMatch = selectedText.match(/^(\s*(?:#{1,4}\s+|> \s*|-\s+))(.*)$/);
                if (blockMatch) {
                    const prefix = blockMatch[1];
                    const actualText = blockMatch[2];
                    newText = text.substring(0, start) + prefix + `*${actualText}*` + text.substring(end);
                    newCursorPos = start + prefix.length + 1;
                } else {
                    newText = text.substring(0, start) + `*${selectedText}*` + text.substring(end);
                    newCursorPos = start + 1;
                }
            }
            break;
        }

        case 'heading': {
            const lineInfo = getLineInfo(text, start);
            const currentLine = lineInfo.currentLine;
            let newLine = currentLine;
            let offset = 0;

            if (currentLine.startsWith('#### ')) {
                newLine = '### ' + currentLine.slice(5);
                offset = -1;
            } else if (currentLine.startsWith('### ')) {
                newLine = '## ' + currentLine.slice(4);
                offset = -1;
            } else if (currentLine.startsWith('## ')) {
                newLine = '# ' + currentLine.slice(3);
                offset = -1;
            } else if (currentLine.startsWith('# ')) {
                newLine = currentLine.slice(2);
                offset = -2;
            } else {
                newLine = '#### ' + currentLine;
                offset = 5;
            }
            newText = text.substring(0, lineInfo.lineStartPosition) + newLine + text.substring(lineInfo.lineEndPosition);
            
            newCursorPos = Math.max(lineInfo.lineStartPosition, start + offset);
            break;
        }

        case 'list':
        case 'quote': {
            const lineInfo = getLineInfo(text, start);
            const currentLine = lineInfo.currentLine;
            
            const marker = type === 'list' ? '-' : '>';
            // Ищем маркер с учетом любых пробелов в начале строки: например "   - текст"
            const regex = new RegExp(`^(\\s*)${marker}\\s+(.*)$`);
            const match = currentLine.match(regex);
            
            let newLine = '';
            let offset = 0;
            
            if (match) {
                // Если форматирование уже есть, убираем маркер, но сохраняем начальные пробелы (match[1]) и сам текст (match[2])
                newLine = match[1] + match[2];
                offset = -2; // Мы удалили маркер и пробел после него (2 символа)
            } else {
                // Если форматирования нет, добавляем маркер после начальных пробелов (чтобы отступы не сбивались)
                const spacesMatch = currentLine.match(/^(\s*)(.*)$/);
                newLine = (spacesMatch ? spacesMatch[1] : '') + `${marker} ` + (spacesMatch ? spacesMatch[2] : currentLine);
                offset = 2; // Мы добавили маркер и пробел (2 символа)
            }
            
            newText = text.substring(0, lineInfo.lineStartPosition) + newLine + text.substring(lineInfo.lineEndPosition);
            newCursorPos = Math.max(lineInfo.lineStartPosition, start + offset);
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
        case 'divider': {
            const lineInfo = getLineInfo(text, start);
            if (lineInfo.currentLine.trim() === '') {
                newText = text.substring(0, lineInfo.lineStartPosition) + '---\n' + text.substring(lineInfo.lineEndPosition);
                newCursorPos = lineInfo.lineStartPosition + 4;
            } else {
                newText = text.substring(0, lineInfo.lineEndPosition) + '\n\n---\n\n' + text.substring(lineInfo.lineEndPosition);
                newCursorPos = lineInfo.lineEndPosition + 6;
            }
            break;
        }
    }

    return { newText, newCursorPos };
};
