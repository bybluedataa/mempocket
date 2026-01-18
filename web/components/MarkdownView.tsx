'use client';

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import Link from 'next/link';

interface MarkdownViewProps {
  content: string;
}

export function MarkdownView({ content }: MarkdownViewProps) {
  // Transform wiki links [[title]] to clickable links
  const transformWikiLinks = (text: string) => {
    return text.replace(/\[\[([^\]]+)\]\]/g, (_, title) => {
      return `[${title}](/entries?search=${encodeURIComponent(title)})`;
    });
  };

  const transformedContent = transformWikiLinks(content);

  return (
    <div className="markdown-content">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          a: ({ href, children }) => {
            if (href?.startsWith('/')) {
              return (
                <Link href={href} className="wiki-link">
                  {children}
                </Link>
              );
            }
            return (
              <a
                href={href}
                target="_blank"
                rel="noopener noreferrer"
                className="text-apple-blue hover:underline"
              >
                {children}
              </a>
            );
          },
          h1: ({ children }) => (
            <h1 className="text-2xl font-semibold mb-4 text-apple-gray-900">
              {children}
            </h1>
          ),
          h2: ({ children }) => (
            <h2 className="text-xl font-semibold mb-3 text-apple-gray-900">
              {children}
            </h2>
          ),
          h3: ({ children }) => (
            <h3 className="text-lg font-semibold mb-2 text-apple-gray-900">
              {children}
            </h3>
          ),
          p: ({ children }) => (
            <p className="mb-4 leading-relaxed text-apple-gray-700">
              {children}
            </p>
          ),
          ul: ({ children }) => (
            <ul className="mb-4 pl-6 list-disc text-apple-gray-700">
              {children}
            </ul>
          ),
          ol: ({ children }) => (
            <ol className="mb-4 pl-6 list-decimal text-apple-gray-700">
              {children}
            </ol>
          ),
          li: ({ children }) => <li className="mb-1">{children}</li>,
          code: ({ className, children }) => {
            const isInline = !className;
            if (isInline) {
              return (
                <code className="bg-apple-gray-100 px-1.5 py-0.5 rounded text-sm text-apple-gray-800">
                  {children}
                </code>
              );
            }
            return (
              <code className={className}>
                {children}
              </code>
            );
          },
          pre: ({ children }) => (
            <pre className="bg-apple-gray-900 text-white p-4 rounded-apple mb-4 overflow-x-auto text-sm">
              {children}
            </pre>
          ),
          blockquote: ({ children }) => (
            <blockquote className="border-l-4 border-apple-gray-200 pl-4 italic text-apple-gray-500 mb-4">
              {children}
            </blockquote>
          ),
          table: ({ children }) => (
            <div className="overflow-x-auto mb-4">
              <table className="min-w-full divide-y divide-apple-gray-200">
                {children}
              </table>
            </div>
          ),
          th: ({ children }) => (
            <th className="px-4 py-2 bg-apple-gray-50 text-left text-sm font-semibold text-apple-gray-700">
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td className="px-4 py-2 text-sm text-apple-gray-600 border-b border-apple-gray-100">
              {children}
            </td>
          ),
        }}
      >
        {transformedContent}
      </ReactMarkdown>
    </div>
  );
}
