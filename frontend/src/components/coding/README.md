# Monaco Editor Integration

This directory contains the Monaco Editor integration for coding questions in the Online Assessment Platform.

## Components

### MonacoCodeEditor
The core Monaco Editor component with TypeScript support, syntax highlighting, and IntelliSense for all supported programming languages.

**Features:**
- Syntax highlighting for Python, JavaScript, TypeScript, Java, C++, C#, Go, and Rust
- Auto-completion and IntelliSense
- Code formatting (Ctrl+Shift+F)
- Error detection and validation
- Auto-save functionality (Ctrl+S)
- Customizable themes (light/dark)
- Responsive design

### CodeExecutionPanel
A panel component that handles code execution and displays results with test case validation.

**Features:**
- Run code execution with output display
- Test case execution with detailed results
- Performance metrics (execution time, memory usage)
- Error handling and display
- Tabbed interface for output and test results

### LanguageSelector
A dropdown component for selecting programming languages.

**Features:**
- Support for all configured programming languages
- Language filtering based on allowed languages
- File extension display
- Disabled state support

### CodingInterface
The main component that combines all coding-related functionality into a complete interface.

**Features:**
- Split-pane layout with resizable panels
- Auto-save functionality (saves after 2 seconds of inactivity)
- Fullscreen mode
- Language switching with starter code
- Code submission handling
- Responsive design for desktop, tablet, and mobile

## Usage

```tsx
import { CodingInterface } from '@/components/coding';

const question: CodingQuestion = {
  id: 'question-1',
  title: 'Two Sum Problem',
  description: 'Find two numbers that add up to target',
  language: 'python',
  starterCode: 'def solution():\n    pass',
  testCases: [
    {
      id: 'test-1',
      input: '[2, 7, 11, 15], 9',
      expectedOutput: '[0, 1]',
      isHidden: false,
      weight: 1.0,
    },
  ],
};

<CodingInterface
  question={question}
  onCodeSubmit={(submission) => console.log('Code submitted:', submission)}
  onAutoSave={(code) => console.log('Auto-saved:', code)}
  showLanguageSelector={true}
  allowedLanguages={['python', 'javascript', 'java']}
/>
```

## Supported Languages

- **Python** (.py) - Python 3.11+
- **JavaScript** (.js) - Node.js 18+
- **TypeScript** (.ts) - TypeScript 5.0+
- **Java** (.java) - Java 17+
- **C++** (.cpp) - GCC 11+
- **C#** (.cs) - .NET 7+
- **Go** (.go) - Go 1.21+
- **Rust** (.rs) - Rust 1.70+

## Configuration

The Monaco Editor can be configured through the following props:

- `theme`: 'light' | 'dark' - Editor theme
- `readOnly`: boolean - Make editor read-only
- `height`: string | number - Editor height
- `language`: SupportedLanguage - Programming language
- `value`: string - Code content
- `onChange`: (value: string) => void - Code change handler

## Auto-save

The coding interface includes auto-save functionality that:
- Saves code after 2 seconds of inactivity
- Provides visual feedback when saving
- Handles save failures gracefully
- Can be disabled by not providing `onAutoSave` prop

## Testing

Run the tests with:

```bash
npm test
```

The components include comprehensive unit tests covering:
- Monaco Editor rendering and interaction
- Language selection and switching
- Code execution simulation
- Auto-save functionality
- Responsive behavior

## Demo

Visit `/coding-demo` to see the Monaco Editor integration in action with a sample coding question.