const express = require('express');
const axios = require('axios');
const bodyParser = require('body-parser');
const app = express();
const port = process.env.PORT || 3000;

app.use(bodyParser.json());
app.use(express.static('public')); // Ensure your HTML and JS files are in the 'public' folder

app.post('/api/get-response', async (req, res) => {
    const userMessage = req.body.message;
    
    // Call to GPT-4o API for response
    try {
        const response = await axios.post('https://api.openai.com/v1/engines/gpt-4o/completions', {
            prompt: userMessage,
            max_tokens: 100
        }, {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer YOUR_OPENAI_API_KEY`
            }
        });

        const botResponse = response.data.choices[0].text.trim();
        res.json({ response: botResponse });
    } catch (error) {
        console.error(error);
        res.status(500).json({ error: 'Error generating response' });
    }
});

app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});
