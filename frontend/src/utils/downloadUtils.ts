// utils/downloadUtils.ts
import pdfMake from "pdfmake/build/pdfmake";
import pdfFonts from "pdfmake/build/vfs_fonts";

(pdfMake as any).addVirtualFileSystem(pdfFonts);

export type DownloadFormat = "txt" | "md" | "docx" | "pdf";

export const convertMarkdownToHtml = (markdown: string): string => {
  let html = markdown;
  
  const codeBlocks: string[] = [];
  html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (_match, language, code) => {
    const placeholder = `%%CODEBLOCK_${codeBlocks.length}%%`;
    codeBlocks.push(`<pre><code class="language-${language || 'plaintext'}">${code.trim()}</code></pre>`);
    return placeholder;
  });
  
  const lines = html.split('\n');
  let result: string[] = [];
  let inTable = false;
  let tableRows: string[] = [];
  let tableSeparator = '|';
  
  for (let i = 0; i < lines.length; i++) {
    let line = lines[i].trim();
    
    if (line.startsWith('%%CODEBLOCK_')) {
      if (inTable) {
        result.push(`<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">${tableRows.join('')}</table>`);
        inTable = false;
        tableRows = [];
      }
      result.push(line);
      continue;
    }
    
    const isPipeSeparator = /^\|[\s\-\|:]+\|$/.test(line);
    const hasTabs = line.includes('\t');
    const isTabSeparator = /^[\-\s\t]+$/.test(line) && hasTabs;
    
    if (isPipeSeparator) {
      tableSeparator = '|';
      if (tableRows.length > 0) {
        const lastRow = tableRows[tableRows.length - 1];
        tableRows[tableRows.length - 1] = lastRow.replace(/<td>/g, '<th>').replace(/<\/td>/g, '</th>');
      }
      continue;
    }
    
    if (isTabSeparator) {
      tableSeparator = '\t';
      if (tableRows.length > 0) {
        const lastRow = tableRows[tableRows.length - 1];
        tableRows[tableRows.length - 1] = lastRow.replace(/<td>/g, '<th>').replace(/<\/td>/g, '</th>');
      }
      continue;
    }

    const isPipeLine = /^\|.+\|$/.test(line);
    const isTabLine = hasTabs && !isTabSeparator;
    
    if (isPipeLine) {
      if (!inTable || tableSeparator !== '|') {
        if (inTable) {
          result.push(`<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">${tableRows.join('')}</table>`);
          tableRows = [];
        }
        inTable = true;
        tableSeparator = '|';
      }
      const cells = line.split('|').map(c => c.trim()).filter((cell, idx, arr) => {
        if ((idx === 0 || idx === arr.length - 1) && cell === '') return false;
        return true;
      });
      
      const cellHtml = cells.map(cell => `<td>${cell}</td>`).join('');
      tableRows.push(`<tr>${cellHtml}</tr>`);
      continue;
    } else if (isTabLine) {
      if (!inTable || tableSeparator !== '\t') {
        if (inTable) {
          result.push(`<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">${tableRows.join('')}</table>`);
          tableRows = [];
        }
        inTable = true;
        tableSeparator = '\t';
      }
      const cells = line.split('\t').filter(cell => cell.trim() !== '');
      const cellHtml = cells.map(cell => `<td>${cell.trim()}</td>`).join('');
      tableRows.push(`<tr>${cellHtml}</tr>`);
      continue;
    } else {
      if (inTable) {
        result.push(`<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">${tableRows.join('')}</table>`);
        inTable = false;
        tableRows = [];
      }
      result.push(line);
    }
  }
  
  if (inTable) {
    result.push(`<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">${tableRows.join('')}</table>`);
  }
  
  html = result.join('\n');

  html = html.replace(/^###### (.+)$/gm, '<h6>$1</h6>');
  html = html.replace(/^##### (.+)$/gm, '<h5>$1</h5>');
  html = html.replace(/^#### (.+)$/gm, '<h4>$1</h4>');
  html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
  html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
  html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');

  html = html.replace(/^---$/gm, '<hr>');
  html = html.replace(/^\*\*\*$/gm, '<hr>');
  html = html.replace(/^___$/gm, '<hr>');

  html = html.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>');
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');

  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');

  html = html.replace(/%%CODEBLOCK_(\d+)%%/g, (match, index) => {
    return codeBlocks[parseInt(index)] || match;
  });

  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

  html = html.replace(/^[\*\-+] (.+)$/gm, '<li>$1</li>');
  html = html.replace(/^\d+\. (.+)$/gm, '<li>$1</li>');

  html = html.replace(/((?:<li>.*<\/li>\n?)+)/g, (match) => {
    return `<ul>${match}</ul>`;
  });

  html = html.replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>');
  html = html.replace(/<\/blockquote>\n<blockquote>/g, '<br>');

  html = html.replace(/^(?!<[hultroblc]|<\/?[hultroblc]|<\/?table|<\/?tr|<\/?t[dh]|<\/?code|<\/?blockquote|<\/?pre)(.+)$/gm, '<p>$1</p>');

  html = html.replace(/<p>\s*<\/p>/g, '<br>');
  
  return html;
};

export const downloadLocally = (format: DownloadFormat, text: string, localTitle: string) => {
  const safeTitle = localTitle.replace(/\s+/g, '_');

  switch (format) {
    case "txt": {
      const content = text;
      const fileName = `${safeTitle}.txt`;
      const mimeType = "text/plain;charset=utf-8";
      const blob = new Blob([content], { type: mimeType });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = fileName;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      break;
    }

    case "md": {
      const content = text;
      const fileName = `${safeTitle}.md`;
      const mimeType = "text/markdown;charset=utf-8";
      const blob = new Blob([content], { type: mimeType });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = fileName;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      break;
    }

    case "docx": {
      const docxHtml = convertMarkdownToHtml(text);
      const content = `
    <html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:w="urn:schemas-microsoft-com:office:word">
    <head>
      <meta charset="UTF-8">
      <title>${localTitle}</title>
      <style>
        body { font-family: Arial, sans-serif; }
        h1 { font-size: 18pt; color: #333; }
        h2 { font-size: 14pt; color: #555; }
        h3 { font-size: 12pt; color: #777; }
        h4 { font-size: 11pt; color: #888; }
        h5 { font-size: 10pt; color: #999; }
        h6 { font-size: 9pt; color: #aaa; }
        table { 
          border-collapse: collapse; 
          width: 100%; 
          margin: 10px 0;
        }
        th {
          background-color: #f0f0f0;
          font-weight: bold;
          border: 1px solid #ddd;
          padding: 8px;
        }
        td { 
          border: 1px solid #ddd; 
          padding: 8px; 
        }
        ul, ol { 
          margin-left: 20px; 
          margin-bottom: 10px;
        }
        li { 
          margin-bottom: 5px; 
        }
        blockquote {
          border-left: 3px solid #ccc;
          padding-left: 10px;
          color: #666;
          margin: 10px 0;
        }
        pre {
          background-color: #f4f4f4;
          padding: 12px;
          font-family: 'Courier New', monospace;
          font-size: 9pt;
        }
        code {
          background-color: #f4f4f4;
          padding: 2px 4px;
          font-family: 'Courier New', monospace;
        }
        p { margin: 5px 0; }
        hr { border: 1px solid #ddd; }
      </style>
    </head>
    <body>
      <h1>${localTitle}</h1>
      ${docxHtml}
    </body>
    </html>`;
      const fileName = `${safeTitle}.doc`;
      const mimeType = "application/msword";
      const blob = new Blob([content], { type: mimeType });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = fileName;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      break;
    }

    case "pdf": {
      const docxHtml = convertMarkdownToHtml(text);
      const fullHtml = `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <title>${localTitle}</title>
        <style>
          body { 
            font-family: Arial, sans-serif; 
            line-height: 1.6; 
            padding: 40px;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
          }
          h1 { font-size: 24pt; margin: 12pt 0 6pt; }
          h2 { font-size: 18pt; margin: 10pt 0 4pt; }
          h3 { font-size: 14pt; margin: 8pt 0 4pt; }
          h4 { font-size: 12pt; margin: 8pt 0 4pt; }
          h5 { font-size: 11pt; margin: 6pt 0 4pt; }
          h6 { font-size: 10pt; margin: 6pt 0 4pt; }
          table { 
            border-collapse: collapse; 
            width: 100%; 
            margin: 10pt 0;
            page-break-inside: avoid;
          }
          th {
            background-color: #f0f0f0;
            font-weight: bold;
            text-align: left;
            border: 1px solid #ddd;
            padding: 8pt;
          }
          td { 
            border: 1px solid #ddd; 
            padding: 8pt; 
            word-wrap: break-word;
          }
          ul { 
            margin-left: 20pt; 
            margin-bottom: 10pt;
            list-style-type: disc;
          }
          ol { 
            margin-left: 20pt; 
            margin-bottom: 10pt;
            list-style-type: decimal;
          }
          li { 
            margin-bottom: 5px; 
          }
          blockquote {
            border-left: 3pt solid #ccc;
            padding-left: 10pt;
            color: #666;
            margin: 10pt 0;
          }
          pre {
            background-color: #f4f4f4;
            padding: 12pt;
            border-radius: 4pt;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 9pt;
            page-break-inside: avoid;
            white-space: pre-wrap;
            word-wrap: break-word;
          }
          code {
            background-color: #f4f4f4;
            padding: 2pt 4pt;
            border-radius: 3pt;
            font-family: 'Courier New', monospace;
            font-size: 9pt;
          }
          pre code {
            background-color: transparent;
            padding: 0;
          }
          p { margin: 5pt 0; }
          hr { 
            border: none;
            border-top: 1pt solid #ddd;
            margin: 15pt 0;
          }
          strong { font-weight: bold; }
          em { font-style: italic; }
          a { color: #0066cc; }
          @media print {
            body { padding: 0; }
            @page { margin: 15mm; }
          }
        </style>
      </head>
      <body>
        <h1>${localTitle}</h1>
        ${docxHtml}
      </body>
      </html>`;
      
      const iframe = document.createElement('iframe');
      iframe.style.position = 'fixed';
      iframe.style.right = '0';
      iframe.style.bottom = '0';
      iframe.style.width = '0';
      iframe.style.height = '0';
      iframe.style.border = '0';
      document.body.appendChild(iframe);
      
      iframe.contentWindow?.document.open();
      iframe.contentWindow?.document.write(fullHtml);
      iframe.contentWindow?.document.close();
      
      setTimeout(() => {
        iframe.contentWindow?.print();
        setTimeout(() => {
          document.body.removeChild(iframe);
        }, 1000);
      }, 500);
      
      break;
    }
  }
};
