import { GoogleGenAI } from "@google/genai";
import readlineSync from "readline-sync";

const ai = new GoogleGenAI({apiKey: "AIzaSyCgKm5U3goeT_L2FmcD2iZZqB1xsQ-svw8"});/// Ab tum GoogleGenAI ko activate kar rahi ho ek API key ke through.

 const chat = ai.chats.create({
    model: "gemini-2.5-flash",
    history: []
  });  // Ab AI ka ek chat session banaya gaya hai.
// Tum keh rahi ho: “Mujhe Gemini-2.5-flash model ke saath baat karni hai, aur filhaal koi history nahi hai.”

async function Chatting(userProblem) {
  
 
}

 async function main(){
  const userProblem = readlineSync.question("Ask me anything--->")
   const response1 = await chat.sendMessage({
  message: userProblem,
  });
  
  console.log(response1.text);
  main()
 }


 main();