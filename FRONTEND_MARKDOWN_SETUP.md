# Frontend Markdown Rendering Setup

Since the backend now streams responses in **markdown format**, your Vercel v0 frontend needs to parse and render markdown.

## Installation

```bash
npm install react-markdown
```

## Usage in Your Chat Component

Replace your raw text display with markdown rendering:

### Before (plain text - WRONG):
```jsx
// This will display markdown as raw text without formatting!
<div className="response-text">
  {message.content}  // ❌ Shows "## Title" literally instead of rendering as header
</div>
```

### After (markdown - CORRECT):
```jsx
import ReactMarkdown from 'react-markdown';

<div className="response-text">
  <ReactMarkdown
    components={{
      h2: ({node, ...props}) => <h2 className="text-lg font-bold mt-4 mb-3 text-blue-600" {...props} />,
      h3: ({node, ...props}) => <h3 className="text-base font-bold mt-3 mb-2" {...props} />,
      ul: ({node, ...props}) => <ul className="list-disc list-inside space-y-2 ml-2" {...props} />,
      li: ({node, ...props}) => <li className="mb-1" {...props} />,
      strong: ({node, ...props}) => <strong className="font-semibold text-gray-900" {...props} />,
      p: ({node, ...props}) => <p className="mb-3 leading-relaxed" {...props} />,
    }}
  >
    {message.content}  // ✅ Renders "## Title" as <h2> tag
  </ReactMarkdown>
</div>
```

**KEY POINT:** If you're still seeing raw markdown text like "## Title" on the screen, you're not using `<ReactMarkdown>`. Switch to it immediately.

## Styling (Tailwind CSS example)

```css
.response-text h2 {
  @apply text-lg font-bold mt-4 mb-2 text-blue-600;
}

.response-text ul {
  @apply list-disc list-inside space-y-1 ml-2;
}

.response-text li {
  @apply mb-1;
}

.response-text strong {
  @apply font-semibold text-gray-900;
}

.response-text p {
  @apply mb-2 leading-relaxed;
}
```

## How the Backend Response Works

### LLM returns this:
```
## My Experience

- **LeadSquared**: Built backend systems for CRM platform
  - Owned auth pipeline, reducing login time by 40%
  - Mentored 2 junior engineers

## Thinking Pattern

- **First Principles**: I break problems into fundamentals
- **High Agency**: I don't wait for permission, I ship
```

### react-markdown renders as:

```
My Experience
═════════════

• LeadSquared: Built backend systems for CRM platform
  - Owned auth pipeline, reducing login time by 40%
  - Mentored 2 junior engineers

Thinking Pattern
════════════════

• First Principles: I break problems into fundamentals
• High Agency: I don't wait for permission, I ship
```

## For Streaming Text

If you're updating the DOM during streaming, ensure you re-render the markdown parser as tokens arrive:

```jsx
const [fullResponse, setFullResponse] = useState("");

// When receiving tokens from SSE:
SSE_source.addEventListener('token', (e) => {
  const token = e.data;
  setFullResponse(prev => prev + token);
  // react-markdown auto-re-renders as state updates
});

<ReactMarkdown>{fullResponse}</ReactMarkdown>
```

## Alternative: Use `react-markdown` with plugins

For better formatting, add `remark-gfm` (GitHub Flavored Markdown):

```bash
npm install remark-gfm
```

```jsx
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

<ReactMarkdown remarkPlugins={[remarkGfm]}>
  {message.content}
</ReactMarkdown>
```

This adds support for:
- Tables
- Strikethrough
- Task lists
- Autolinks

## Testing

Test with this sample markdown:

```markdown
## Experience

- **Company A**: Description here
  - Impact: Metric
  
## Skills

- **Backend**: Python, Go, Java
- **AI/ML**: LangGraph, RAG, tool-calling

## Mindset

I believe in **first principles thinking** and moving at *speed*.
```

Copy-paste this into your frontend and you should see nice formatting automatically.

## Notes

- Backend will format responses; frontend just needs to render
- Markdown is streamed character-by-character (react-markdown handles incremental updates)
- No additional backend changes needed
- This is the standard pattern used by ChatGPT, Claude, etc.
