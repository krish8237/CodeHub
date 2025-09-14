import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MonacoCodeEditor } from '../MonacoCodeEditor';

// Mock Monaco Editor
vi.mock('@monaco-editor/react', () => ({
  Editor: ({ value, onChange, language }: any) => (
    <div data-testid="monaco-editor">
      <div data-testid="editor-language">{language}</div>
      <textarea
        data-testid="editor-textarea"
        value={value}
        onChange={(e) => onChange?.(e.target.value)}
      />
    </div>
  ),
}));

describe('MonacoCodeEditor', () => {
  const mockOnChange = vi.fn();

  beforeEach(() => {
    mockOnChange.mockClear();
  });

  it('renders Monaco Editor with correct props', () => {
    const testCode = 'console.log("Hello, World!");';
    
    render(
      <MonacoCodeEditor
        value={testCode}
        onChange={mockOnChange}
        language="javascript"
      />
    );

    expect(screen.getByTestId('monaco-editor')).toBeInTheDocument();
    expect(screen.getByTestId('editor-language')).toHaveTextContent('javascript');
    expect(screen.getByTestId('editor-textarea')).toHaveValue(testCode);
  });

  it('calls onChange when code is modified', async () => {
    const { user } = render(
      <MonacoCodeEditor
        value=""
        onChange={mockOnChange}
        language="python"
      />
    );

    const textarea = screen.getByTestId('editor-textarea');
    await user.type(textarea, 'print("Hello")');

    expect(mockOnChange).toHaveBeenCalled();
  });

  it('renders with different languages', () => {
    const { rerender } = render(
      <MonacoCodeEditor
        value=""
        onChange={mockOnChange}
        language="python"
      />
    );

    expect(screen.getByTestId('editor-language')).toHaveTextContent('python');

    rerender(
      <MonacoCodeEditor
        value=""
        onChange={mockOnChange}
        language="java"
      />
    );

    expect(screen.getByTestId('editor-language')).toHaveTextContent('java');
  });

  it('handles readOnly prop correctly', () => {
    render(
      <MonacoCodeEditor
        value="const x = 1;"
        onChange={mockOnChange}
        language="typescript"
        readOnly={true}
      />
    );

    const textarea = screen.getByTestId('editor-textarea');
    expect(textarea).toBeInTheDocument();
  });
});