import React, { useRef, useEffect, useCallback } from 'react';
import { Editor, OnMount, OnChange } from '@monaco-editor/react';
import { editor } from 'monaco-editor';
import { Box, useTheme } from '@mui/material';
import { SupportedLanguage } from '../../types/coding';

interface MonacoCodeEditorProps {
  value: string;
  onChange: (value: string) => void;
  language: SupportedLanguage;
  height?: string | number;
  readOnly?: boolean;
  theme?: 'light' | 'dark';
  onMount?: (editor: editor.IStandaloneCodeEditor) => void;
}

export const MonacoCodeEditor: React.FC<MonacoCodeEditorProps> = ({
  value,
  onChange,
  language,
  height = '400px',
  readOnly = false,
  theme,
  onMount,
}) => {
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);
  const muiTheme = useTheme();
  
  // Determine theme based on MUI theme if not explicitly provided
  const editorTheme = theme || (muiTheme.palette.mode === 'dark' ? 'vs-dark' : 'vs');

  const handleEditorDidMount: OnMount = useCallback((editor, monaco) => {
    editorRef.current = editor;
    
    // Configure editor options
    editor.updateOptions({
      fontSize: 14,
      fontFamily: 'Fira Code, Monaco, Consolas, "Courier New", monospace',
      lineNumbers: 'on',
      roundedSelection: false,
      scrollBeyondLastLine: false,
      readOnly,
      minimap: { enabled: true },
      folding: true,
      lineDecorationsWidth: 10,
      lineNumbersMinChars: 3,
      glyphMargin: false,
      automaticLayout: true,
      wordWrap: 'on',
      wrappingIndent: 'indent',
      formatOnPaste: true,
      formatOnType: true,
      autoIndent: 'full',
      tabSize: 4,
      insertSpaces: true,
      detectIndentation: true,
      trimAutoWhitespace: true,
      renderWhitespace: 'selection',
      renderControlCharacters: false,
      renderIndentGuides: true,
      highlightActiveIndentGuide: true,
      bracketPairColorization: { enabled: true },
      guides: {
        bracketPairs: true,
        indentation: true,
      },
    });

    // Configure language-specific settings
    configureLanguageFeatures(monaco, language);
    
    // Add keyboard shortcuts
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
      // Auto-save functionality will be handled by parent component
      const currentValue = editor.getValue();
      onChange(currentValue);
    });

    // Format document shortcut
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyMod.Shift | monaco.KeyCode.KeyF, () => {
      editor.getAction('editor.action.formatDocument')?.run();
    });

    // Call parent onMount if provided
    if (onMount) {
      onMount(editor);
    }
  }, [language, readOnly, onMount, onChange]);

  const handleEditorChange: OnChange = useCallback((value) => {
    if (value !== undefined) {
      onChange(value);
    }
  }, [onChange]);

  // Configure language-specific features
  const configureLanguageFeatures = (monaco: any, lang: SupportedLanguage) => {
    switch (lang) {
      case 'python':
        monaco.languages.setLanguageConfiguration('python', {
          indentationRules: {
            increaseIndentPattern: /^\s*(def|class|if|elif|else|for|while|with|try|except|finally|async def).*:\s*$/,
            decreaseIndentPattern: /^\s*(elif|else|except|finally)\b.*$/,
          },
        });
        break;
      case 'javascript':
      case 'typescript':
        monaco.languages.setLanguageConfiguration(lang, {
          autoClosingPairs: [
            { open: '{', close: '}' },
            { open: '[', close: ']' },
            { open: '(', close: ')' },
            { open: '"', close: '"' },
            { open: "'", close: "'" },
            { open: '`', close: '`' },
          ],
        });
        break;
      case 'java':
      case 'csharp':
        monaco.languages.setLanguageConfiguration(lang === 'java' ? 'java' : 'csharp', {
          autoClosingPairs: [
            { open: '{', close: '}' },
            { open: '[', close: ']' },
            { open: '(', close: ')' },
            { open: '"', close: '"' },
          ],
        });
        break;
    }
  };

  // Auto-resize editor when container size changes
  useEffect(() => {
    const handleResize = () => {
      if (editorRef.current) {
        editorRef.current.layout();
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <Box
      sx={{
        height,
        border: 1,
        borderColor: 'divider',
        borderRadius: 1,
        overflow: 'hidden',
        '& .monaco-editor': {
          '& .margin': {
            backgroundColor: 'transparent',
          },
        },
      }}
    >
      <Editor
        height={height}
        language={getMonacoLanguage(language)}
        value={value}
        theme={editorTheme}
        onChange={handleEditorChange}
        onMount={handleEditorDidMount}
        options={{
          selectOnLineNumbers: true,
          automaticLayout: true,
        }}
      />
    </Box>
  );
};

// Map our language IDs to Monaco language IDs
const getMonacoLanguage = (language: SupportedLanguage): string => {
  const languageMap: Record<SupportedLanguage, string> = {
    python: 'python',
    javascript: 'javascript',
    typescript: 'typescript',
    java: 'java',
    cpp: 'cpp',
    csharp: 'csharp',
    go: 'go',
    rust: 'rust',
  };
  
  return languageMap[language] || 'plaintext';
};