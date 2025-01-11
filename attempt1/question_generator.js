const form = document.querySelector('form');

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    console.log("Il n’y a pas eu de rechargement de page");
    const url = document.getElementById("URL").value;
    const nquestions = document.getElementById("nquestions").value;
    const response = await fetch(url, {
        method : 'GET',
        mode:  'cors',
        headers: {
            "Content-Type": "text/xml"
        }
    })
    // const parsed_responses = await response.json()
    console.log(response)
});


// var theText = $('article').text();

// import { Mistral } from '@mistralai/mistralai';
// const apiKey = process.env.MISTRAL_API_KEY;

// const client = new Mistral({apiKey: apiKey});

// const chatResponse = await client.chat.complete({
//   model: 'mistral-large-latest',
//   messages: [{role: 'user', content: 'What is the best French cheese?'}],
// });

// console.log('Chat:', chatResponse.choices[0].message.content);