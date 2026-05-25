import React from "react";


export const highlightText = (text: string, highlight: string): React.JSX.Element => {
  if (!highlight.trim()) return <>{text}</>;

  const words = highlight
    .trim()
    .split(/\s+/)
    .map(word => word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'))
    .filter(word => word.length >= 2); 

  if (words.length === 0) return <>{text}</>;

  const stems = words.map(word => {
    if (word.length > 5) return word.substring(0, word.length - 2); 
    if (word.length > 3) return word.substring(0, word.length - 1);
    return word;
  });

  const sortedStems = stems.sort((a, b) => b.length - a.length);


  const regexPattern = sortedStems
    .map(stem => `[A-Za-zА-Яа-яЁё]*${stem}[A-Za-zА-Яа-яЁё]*`)
    .join('|');

  if (!regexPattern) return <>{text}</>;


  const parts = text.split(new RegExp(`(${regexPattern})`, 'gi'));

  return (
    <>
      {parts.map((part, index) => {
        const isMatch = sortedStems.some(stem => 
          part.toLowerCase().includes(stem.toLowerCase())
        );

        return isMatch ? (
          <span 
            key={index} 
            style={{ 
              backgroundColor: 'color-mix(in srgb, var(--color-text-purple) 25%, transparent)',
              color: 'var(--color-text-purple)',
              fontWeight: 600,
              borderRadius: '4px',
              padding: '0 2px'
            }}
          >
            {part}
          </span>
        ) : (
          <span key={index}>{part}</span>
        );
      })}
    </>
  );
};