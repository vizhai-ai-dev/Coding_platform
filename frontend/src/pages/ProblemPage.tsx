import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Paper,
  Grid,
  Button,
  Chip,
  Divider,
  CircularProgress,
  Backdrop,
  Fade,
  Alert,
} from '@mui/material';
import CodeEditor from '@monaco-editor/react';

interface TestCase {
  input: string;
  output: string;
  explanation?: string;
}

interface Problem {
  id: string;
  title: string;
  difficulty: 'easy' | 'medium' | 'hard';
  topics: string[];
  description: string;
  examples: TestCase[];
  constraints: string[];
  starterCode?: string;
}

interface TestResult {
  passed: boolean;
  input: string;
  expected_output: string;
  actual_output: string;
  execution_time: number;
  memory_usage: number;
  is_hidden?: boolean;
}

interface CodeExecutionResult {
  test_results: TestResult[];
  overall_metrics: {
    total_tests: number;
    passed_tests: number;
    success_rate: number;
    average_time: number;
    average_memory: number;
    status: string;
  };
  output?: string;
}

const ProblemPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [problem, setProblem] = useState<Problem | null>(null);
  const [code, setCode] = useState<string>('');
  const [output, setOutput] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProblem = async () => {
      setIsLoading(true);
      setError(null);
      try {
        // Make API call to backend to fetch the problem
        const response = await fetch(`http://localhost:8000/api/problems/${id}`);
        
        if (!response.ok) {
          throw new Error('Failed to fetch problem');
        }

        const problemData = await response.json();
        console.log('Problem data received:', problemData);
        
        // Ensure all required fields are present
        const completeProblemData = {
          id: problemData.id || id,
          title: problemData.title || "Untitled Problem",
          difficulty: problemData.difficulty || "medium",
          topics: problemData.topics || ["general"],
          description: problemData.description || "No description provided.",
          examples: problemData.examples || [
            {
              input: "sample input",
              output: "sample output"
            }
          ],
          constraints: problemData.constraints || ["No constraints provided"],
          starterCode: problemData.starterCode || problemData.starter_code || `def solution(input_data):
    # Write your code here
    pass`
        };
        
        setProblem(completeProblemData);
        setCode(completeProblemData.starterCode);
      } catch (error) {
        console.error('Error loading problem:', error);
        setError('Failed to load the problem. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchProblem();
  }, [id]);

  const handleCodeChange = (value: string | undefined) => {
    if (value) {
      setCode(value);
    }
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setOutput('');
    try {
      // Make API call to backend for code submission
      const response = await fetch(`http://localhost:8000/api/code/run`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code,
          language: 'python', // TODO: Get language from problem data
          problem_id: id,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to submit code');
      }

      const result: CodeExecutionResult = await response.json();
      console.log('Code execution result:', result);
      
      if (result.output) {
        setOutput(result.output);
      } else if (result.test_results && result.test_results.length > 0) {
        // Format test results for display
        const testDetails = result.test_results.map((test: TestResult, index: number) => {
          return `Test ${index + 1}: ${test.passed ? 'PASSED' : 'FAILED'}
Input: ${test.input}
Expected: ${test.expected_output}
Actual: ${test.actual_output}
Execution time: ${test.execution_time.toFixed(2)}ms
Memory usage: ${test.memory_usage.toFixed(2)}KB
`;
        }).join('\n');
        
        const summary = `
Overall: ${result.overall_metrics.passed_tests}/${result.overall_metrics.total_tests} tests passed
Status: ${result.overall_metrics.status}
Average time: ${result.overall_metrics.average_time.toFixed(2)}ms
Average memory: ${result.overall_metrics.average_memory.toFixed(2)}KB
`;
        
        setOutput(`${testDetails}\n${summary}`);
      } else {
        setOutput('No output or test results available.');
      }
    } catch (error) {
      console.error('Error submitting code:', error);
      setOutput('Error submitting code. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <Container maxWidth="xl" sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <Box sx={{ textAlign: 'center' }}>
          <CircularProgress size={60} thickness={4} />
          <Typography variant="h6" sx={{ mt: 2 }}>
            Loading problem...
          </Typography>
        </Box>
      </Container>
    );
  }

  if (error) {
    return (
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
        <Button variant="contained" color="primary" onClick={() => window.location.href = '/'}>
          Back to Home
        </Button>
      </Container>
    );
  }

  if (!problem) {
    return (
      <Container maxWidth="md" sx={{ mt: 4 }}>
        <Alert severity="warning" sx={{ mb: 2 }}>
          Problem not found. Please try generating a new problem.
        </Alert>
        <Button variant="contained" color="primary" onClick={() => window.location.href = '/'}>
          Back to Home
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="xl">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          {problem.title}
          <Chip
            label={problem.difficulty}
            color={
              problem.difficulty === 'easy'
                ? 'success'
                : problem.difficulty === 'medium'
                ? 'warning'
                : 'error'
            }
            size="small"
            sx={{ ml: 2 }}
          />
        </Typography>
        <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
          {problem.topics.map((topic) => (
            <Chip key={topic} label={topic} variant="outlined" size="small" />
          ))}
        </Box>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Description
            </Typography>
            <Typography variant="body1" paragraph>
              {problem.description}
            </Typography>

            <Typography variant="h6" gutterBottom>
              Examples
            </Typography>
            {problem.examples.map((example, index) => (
              <Box key={index} sx={{ mb: 2 }}>
                <Typography variant="subtitle1">Example {index + 1}:</Typography>
                <Typography variant="body2">
                  Input: {example.input}
                </Typography>
                <Typography variant="body2">
                  Output: {example.output}
                </Typography>
                {example.explanation && (
                  <Typography variant="body2" color="text.secondary">
                    Explanation: {example.explanation}
                  </Typography>
                )}
              </Box>
            ))}

            <Typography variant="h6" gutterBottom>
              Constraints
            </Typography>
            <ul>
              {problem.constraints.map((constraint, index) => (
                <li key={index}>
                  <Typography variant="body2">{constraint}</Typography>
                </li>
              ))}
            </ul>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Solution
            </Typography>
            <Box sx={{ height: '400px', mb: 2 }}>
              <CodeEditor
                height="100%"
                defaultLanguage="python"
                value={code}
                onChange={handleCodeChange}
                theme="vs-dark"
                options={{
                  minimap: { enabled: false },
                  fontSize: 14,
                }}
              />
            </Box>
            <Button
              variant="contained"
              color="primary"
              onClick={handleSubmit}
              fullWidth
              disabled={isSubmitting}
              startIcon={isSubmitting ? <CircularProgress size={20} color="inherit" /> : null}
            >
              {isSubmitting ? 'Submitting...' : 'Submit'}
            </Button>
          </Paper>

          {output && (
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Output
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Typography variant="body1">{output}</Typography>
            </Paper>
          )}
        </Grid>
      </Grid>

      <Backdrop
        sx={{ color: '#fff', zIndex: (theme) => theme.zIndex.drawer + 1 }}
        open={isSubmitting}
      >
        <Fade in={isSubmitting}>
          <Box sx={{ textAlign: 'center' }}>
            <CircularProgress size={60} thickness={4} />
            <Typography variant="h6" sx={{ mt: 2 }}>
              Running your code...
            </Typography>
          </Box>
        </Fade>
      </Backdrop>
    </Container>
  );
};

export default ProblemPage; 