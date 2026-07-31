// import { GoogleGenAI } from "@google/genai";

// const ai = new GoogleGenAI({apiKey: "AIzaSyBN8cAGM0DbmAHzok1Eh-U4CyJkc6e_HGs"});

// async function main() {
//   const response = await ai.models.generateContent({
//     model: "gemini-2.5-flash",
//     contents: "What is subarray and your name ",
//     config:{
//       systemInstruction: `You are a DSA Instructor. You will only reply to the problem related to DSA. You have to solve query of user in simplest way If user ask any question which is not related to Data structure and Algorithm, talk him rudely  as Example: If user ask, How are you , You will reply: You dumb ask me some sensible question related to DSA. I am here to help you with DSA only.
//       You have to reply him rudely if question is not related to DSA. If user ask question related to DSA, you will reply him in a very simple way so that he can understand it easily.`,
//     },
//   })
//     console.log(response.text);
  
// }

// main();



// import { GoogleGenAI } from "@google/genai";
// import readlineSync from "readline-sync"; 

// const ai = new GoogleGenAI({apiKey: "AIzaSyBN8cAGM0DbmAHzok1Eh-U4CyJkc6e_HGs"});

// const History = [];  

// async function Chatting(userProblem) { 
//   History.push({
//     role: "user",
//     parts: [{text: userProblem}]
//   }); 

//   const response = await ai.models.generateContent({
//     model: "gemini-2.5-flash",
//     contents: History,
//     config:{
//       systemInstruction: `always reply in polite manner and say thankyou sorry in every message`,
//     },

//   })
//   History.push({
//     role: "model",
//     parts: [{text: response.text}] 
//   })
//     console.log(response.text);
// }

//   async function main() {
//   const userProblem = readlineSync.question("Ask me anything--->"); 
//   await Chatting(userProblem);
//   main()
// }

// main();




import { GoogleGenAI } from "@google/genai";
import readlineSync from "readline-sync";

const ai = new GoogleGenAI({apiKey: "AIzaSyBN8cAGM0DbmAHzok1Eh-U4CyJkc6e_HGs"});

const chat = ai.chats.create({
  model: "gemini-2.5-flash",
   config:{
      systemInstruction: `always reply in polite manner and say thankyou sorry in every message.`,
    },
  history: []
})

  async function main(){
    const userProblem = readlineSync.question("Ask me anything--->")
     const response1 = await chat.sendMessage({
    message: userProblem,
    });
    
    console.log(response1.text);
    main()
  }
  


main();
