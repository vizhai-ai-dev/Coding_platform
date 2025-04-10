import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Paper,
  CircularProgress,
  Backdrop,
  Fade,
  Alert,
  Snackbar,
} from '@mui/material';

const Home: React.FC = () => {
  const navigate = useNavigate();
  const [topic, setTopic] = useState('arrays');
  const [difficulty, setDifficulty] = useState('medium');
  const [language, setLanguage] = useState('python');
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleGenerateProblem = async () => {
    setIsGenerating(true);
    setError(null);
    try {
      console.log('Generating problem with:', { topic, difficulty });
      
      // Make API call to backend for problem generation
      const response = await fetch(`http://localhost:8000/api/problems/generate?topic=${topic}&difficulty=${difficulty}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();
      console.log('Problem generated:', data);
      
      if (!data || !data.id) {
        console.error('Invalid problem data received:', data);
        throw new Error('Invalid problem data received from server');
      }
      
      // Navigate to the problem page
      navigate(`/problem/${data.id}`);
    } catch (error) {
      console.error('Error generating problem:', error);
      setError(error instanceof Error ? error.message : 'Failed to generate problem');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Welcome to the Coding Platform
        </Typography>
        <Typography variant="body1" paragraph>
          Generate coding problems and practice your skills with our interactive platform.
        </Typography>
      </Box>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Generate a New Problem
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <FormControl sx={{ minWidth: 200 }}>
            <InputLabel>Topic</InputLabel>
            <Select
              value={topic}
              label="Topic"
              onChange={(e) => setTopic(e.target.value)}
              disabled={isGenerating}
            >
              <MenuItem value="arrays">Arrays</MenuItem>
              <MenuItem value="strings">Strings</MenuItem>
              <MenuItem value="trees">Trees</MenuItem>
              <MenuItem value="graphs">Graphs</MenuItem>
              <MenuItem value="dp">Dynamic Programming</MenuItem>
            </Select>
          </FormControl>

          <FormControl sx={{ minWidth: 200 }}>
            <InputLabel>Difficulty</InputLabel>
            <Select
              value={difficulty}
              label="Difficulty"
              onChange={(e) => setDifficulty(e.target.value)}
              disabled={isGenerating}
            >
              <MenuItem value="easy">Easy</MenuItem>
              <MenuItem value="medium">Medium</MenuItem>
              <MenuItem value="hard">Hard</MenuItem>
            </Select>
          </FormControl>

          <FormControl sx={{ minWidth: 200 }}>
            <InputLabel>Language</InputLabel>
            <Select
              value={language}
              label="Language"
              onChange={(e) => setLanguage(e.target.value)}
              disabled={isGenerating}
            >
              <MenuItem value="python">Python</MenuItem>
              <MenuItem value="javascript">JavaScript</MenuItem>
              <MenuItem value="java">Java</MenuItem>
            </Select>
          </FormControl>
        </Box>

        <Box sx={{ mt: 3 }}>
          <Button
            variant="contained"
            color="primary"
            onClick={handleGenerateProblem}
            size="large"
            disabled={isGenerating}
            startIcon={isGenerating ? <CircularProgress size={20} color="inherit" /> : null}
          >
            {isGenerating ? 'Generating...' : 'Generate Problem'}
          </Button>
        </Box>
      </Paper>

      <Backdrop
        sx={{ color: '#fff', zIndex: (theme) => theme.zIndex.drawer + 1 }}
        open={isGenerating}
      >
        <Fade in={isGenerating}>
          <Box sx={{ textAlign: 'center' }}>
            <CircularProgress size={60} thickness={4} />
            <Typography variant="h6" sx={{ mt: 2 }}>
              Generating your problem...
            </Typography>
            <Typography variant="body2" sx={{ mt: 1, maxWidth: 400 }}>
              Our AI is creating a unique coding challenge based on your selected parameters.
              This may take a few moments.
            </Typography>
          </Box>
        </Fade>
      </Backdrop>

      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError(null)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={() => setError(null)} severity="error" sx={{ width: '100%' }}>
          {error}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default Home; 