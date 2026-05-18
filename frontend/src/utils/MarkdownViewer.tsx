import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MarkdownViewerProps {
  content: string;
}

export default function MarkdownViewer({ content }: MarkdownViewerProps) {
  if (!content?.trim()) return null;

  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        h1: ({node, ref, ...props}: any) => <h2 className="text-2xl font-bold mt-5 mb-3 text-[var(--color-text-primary)]" {...props} />,
        h2: ({node, ref, ...props}: any) => <h3 className="text-xl font-bold mt-4 mb-2 text-[var(--color-text-primary)]" {...props} />,
        h3: ({node, ref, ...props}: any) => <h4 className="text-lg font-bold mt-3 mb-2 text-[var(--color-text-primary)]" {...props} />,
        h4: ({node, ref, ...props}: any) => <h5 className="text-base font-bold mt-2 mb-1 text-[var(--color-text-primary)]" {...props} />,
        
        p: ({node, ref, ...props}: any) => <p className="mb-3 text-[var(--color-text-primary)] leading-relaxed" {...props} />,
        strong: ({node, ref, ...props}: any) => <strong className="font-bold text-[var(--color-text-primary)]" {...props} />,
        em: ({node, ref, ...props}: any) => <em className="italic text-[var(--color-text-secondary)]" {...props} />,
        
        a: ({node, ref, ...props}: any) => (
          <a 
            className="text-[var(--color-text-purple)] hover:opacity-80 underline" 
            target="_blank" 
            rel="noopener noreferrer" 
            {...props} 
          />
        ),
        
        blockquote: ({node, ref, ...props}: any) => (
          <blockquote className="border-l-4 border-[var(--color-text-purple)] pl-4 my-2 text-[var(--color-text-secondary)] italic" {...props} />
        ),
        
        ul: ({node, ref, ...props}: any) => <ul className="my-2 list-inside" {...props} />,
        ol: ({node, ref, ...props}: any) => <ol className="my-2 list-decimal list-inside" {...props} />,
        li: ({node, ref, ...props}: any) => <li className="ml-4 text-[var(--color-text-primary)] mb-1 list-disc" {...props} />,
        
        hr: ({node, ref, ...props}: any) => <hr className="my-6 border-t-2 border-[var(--color-border)] opacity-50" {...props} />
      }}
    >
      {content}
    </ReactMarkdown>
  );
}
