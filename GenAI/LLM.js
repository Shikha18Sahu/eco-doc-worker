import { GoogleGenAI } from "@google/genai";   //GoogleGenAI class ko @google/genai package se import karti hai.
import readlineSync from "readline-sync";  //User se text input lene ke liye ek tool le rahe hain.

const ai = new GoogleGenAI({apiKey: "AIzaSyCgKm5U3goeT_L2FmcD2iZZqB1xsQ-svw8"});

const History = [];  // Ek khaali array banaya gaya hai, jisme hum user aur AI ke saare conversation store karenge.

async function Chatting(userProblem) {  //Ek async function banaya gaya hai jo AI se baat karta hai. userProblem ka matlab user ka sawal hai

  History.push({
    role: "user",
    parts: [{text: userProblem}]
  });  // User ka question history mein add kiya ja raha hai.

  

  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash",
    contents: History
  }); //AI se reply liya ja raha hai using Gemini-2.5-flash model. History bhi bheji ja rahi hai taaki AI context samjhe.

   History.push({
    role: "model",
    parts: [{text: response.text}]  //AI ka reply bhi history mein add kiya ja raha hai.
  });
  console.log("/n")
  

  console.log(response.text); //AI ka final reply print kiya ja raha hai.
}

 async function main(){  // Ek main function jo sab kuch control karega.

  const userProblem = readlineSync.question("Ask me anything--->") // Yeh ek module hai jo tumhare terminal ya console se user se input lene ka kaam karta hai.

  await Chatting(userProblem); //Abhi liya hua input AI ko bhej diya gaya aur uska reply liya gaya.
  
  main()   //Yeh main() ko dobara call karta hai — taaki loop chalta rahe (infinite chat).
 }

 main(); // Pehli baar program chalane ke liye main() call kiya gaya.