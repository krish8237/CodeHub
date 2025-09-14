import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Button,
  Alert,
} from '@mui/material';
import { CodingInterface } from '../components/coding';
import { CodingQuestion, CodeSubmission } from '../types/coding';

// Mock coding question for demo
const mockCodingQuestion: CodingQuestion = {
  id: 'demo-question-1',
  title: 'Two Sum Problem',
  description: 'Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target. You may assume that each input would have exactly one solution, and you may not use the same element twice.',
  language: 'python',
  starterCode: `def two_sum(nums, target):
    """
    Find two numbers in the array that add up to target.
    
    Args:
        nums: List of integers
        target: Target sum
        
    Returns:
        List of two indices
    """
    # Write your solution here
    pass

# Test your solution
if __name__ == "__main__":
    nums = [2, 7, 11, 15]
    target = 9
    result = two_sum(nums, target)
    print(f"Indices: {result}")`,
  testCases: [
    {
      id: 'test-1',
      input: 'nums = [2, 7, 11, 15], target = 9',
      expectedOutput: '[0, 1]',
      isHidden: false,
      weight: 1.0,
    },
    {
      id: 'test-2',
      input: 'nums = [3, 2, 4], target = 6',
      expectedOutput: '[1, 2]',
      isHidden: false,
      weight: 1.0,
    },
    {
      id: 'test-3',
      input: 'nums = [3, 3], target = 6',
      expectedOutput: '[0, 1]',
      isHidden: false,
      weight: 1.0,
    },
    {
      id: 'test-4',
      input: 'nums = [1, 2, 3, 4, 5], target = 8',
      expectedOutput: '[2, 4]',
      isHidden: true,
      weight: 2.0,
    },
  ],
  timeLimit: 300, // 5 minutes
  memoryLimit: 128, // 128MB
};

export const CodingDemoPage: React.FC = () => {
  const [submissions, setSubmissions] = useState<CodeSubmission[]>([]);
  const [autoSaveStatus, setAutoSaveStatus] = useState<string>('');

  const handleCodeSubmit = (submission: CodeSubmission) => {
    setSubmissions(prev => [...prev, submission]);
    console.log('Code submitted:', submission);
  };

  const handleAutoSave = (code: string) => {
    setAutoSaveStatus(`Auto-saved at ${new Date().toLocaleTimeString()}`);
    console.log('Auto-saved code:', code.length, 'characters');
    
    // Clear status after 3 seconds
    setTimeout(() => {
      setAutoSaveStatus('');
    }, 3000);
  };

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Monaco Editor Integration Demo
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          This demo showcases the Monaco Editor integration with code execution capabilities.
          The editor includes syntax highlighting, IntelliSense, auto-completion, and error detection
          for multiple programming languages.
        </Typography>
        
        {autoSaveStatus && (
          <Alert severity="success" sx={{ mb: 2 }}>
            {autoSaveStatus}
          </Alert>
        )}
      </Box>

      <Paper elevation={2} sx={{ p: 3, mb: 4 }}>
        <Typography variant="h5" gutterBottom>
          Features Demonstrated:
        </Typography>
        <Box component="ul" sx={{ pl: 3 }}>
          <Typography component="li" variant="body2" gutterBottom>
            Monaco Editor with TypeScript support and syntax highlighting
          </Typography>
          <Typography component="li" variant="body2" gutterBottom>
            Language selector with support for Python, JavaScript, TypeScript, Java, C++, C#, Go, and Rust
          </Typography>
          <Typography component="li" variant="body2" gutterBottom>
            Code formatting, auto-completion, and error detection
          </Typography>
          <Typography component="li" variant="body2" gutterBottom>
            Split-pane layout with code editor and execution results
          </Typography>
          <Typography component="li" variant="body2" gutterBottom>
            Run code and test execution with detailed results
          </Typography>
          <Typography component="li" variant="body2" gutterBottom>
            Auto-save functionality (saves after 2 seconds of inactivity)
          </Typography>
          <Typography component="li" variant="body2" gutterBottom>
            Fullscreen mode for distraction-free coding
          </Typography>
          <Typography component="li" variant="body2" gutterBottom>
            Responsive design that works on desktop, tablet, and mobile
          </Typography>
        </Box>
      </Paper>

      <CodingInterface
        question={mockCodingQuestion}
        onCodeSubmit={handleCodeSubmit}
        onAutoSave={handleAutoSave}
        showLanguageSelector={true}
        allowedLanguages={['python', 'javascript', 'typescript', 'java', 'cpp']}
      />

      {submissions.length > 0 && (
        <Paper elevation={1} sx={{ p: 3, mt: 4 }}>
          <Typography variant="h6" gutterBottom>
            Submission History ({submissions.length})
          </Typography>
          {submissions.map((submission, index) => (
            <Box key={index} sx={{ mb: 2, p: 2, bgcolor: 'grey.50', borderRadius: 1 }}>
              <Typography variant="body2" color="text.secondary">
                Submitted at: {submission.timestamp.toLocaleString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Language: {submission.language}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Code length: {submission.code.length} characters
              </Typography>
            </Box>
          ))}
        </Paper>
      )}

      <Box sx={{ mt: 4, textAlign: 'center' }}>
        <Button
          variant="outlined"
          onClick={() => window.location.reload()}
        >
          Reset Demo
        </Button>
      </Box>
    </Container>
  );
};