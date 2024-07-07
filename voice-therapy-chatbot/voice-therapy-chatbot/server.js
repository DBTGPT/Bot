const express = require('express');
const axios = require('axios');
const bodyParser = require('body-parser');
const app = express();
const port = process.env.PORT || 3000;

app.use(bodyParser.json());
app.use(express.static('public'));

app.post('/api/get-response', async (req, res) => {
    const userMessage = req.body.message;

    try {
        const response = await axios.post('https://api.openai.com/v1/chat/completions', {
            model: 'gpt-4-0613', // Use the latest model version
            messages: [{ role: 'user', content: userMessage }],
            max_tokens: 100
        }, {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer YOUR_OPENAI_API_KEY`
            }
        });

        console.log('API response:', response.data);

        if (response.data && response.data.choices && response.data.choices.length > 0) {
            const botResponse = response.data.choices[0].message.content.trim();
            res.json({ response: botResponse });
        } else {
            res.json({ response: 'Sorry, I couldn\'t understand that. Could you please repeat?' });
        }
    } catch (error) {
        console.error('Error generating response:', error);
        res.status(500).json({ error: 'Error generating response' });
    }
});

app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});
