import { GoogleGenAI } from '@google/genai';
import readlineSync from 'readline-sync';
const ai = new GoogleGenAI({apiKey:"AIzaSyAHAeb_DYUGn0YNrbLvPnH4b8gzSiWddi4"});

const History = []

function sum({num1, num2}){
  return num1 + num2;
}


function prime({num}){
  if(num<2)
    return false;
 for(let i = 2; i <= Math.sqrt(num); i++){
    if(num % i == 0)
      return false;
  }
  return true;
}


async function getCryptoPrice({coin}){

const response = await fetch(`https://api.coingecko.com/api/v3/coins/market?vs_currency=usd&ids=${coin}`);
const data = await response.json();
return data;
}

// 7 and 5 ka sum kya hai aur 13  prime Number hai ya nai 
// [
//   {
//   name: "sum", 
//   args: {num1: 7, num2: 5}
//   },
//   {
//    name: 'prime',
//    args: {num: 13}
//   }
// ]

const sumDeclaration = {
  name: "sum",
  description: "Returns the sum of two numbers",
  parameters: {
    type: "OBJECT",
    properties: {
      num1: {
        type: "NUMBER",
        description: "The first number to sum"
      },
      num2: {
        type: "NUMBER",
        description: "The second number to sum"
      }
    },
    required: ["num1", "num2"]
  }
}
 

const primeDeclaration = {
  name: "prime",
  description: "Get if number if prime or not",
  parameters: {
    type: "OBJECT",
    properties: {
      num: {
        type: "NUMBER",
        description: "It will be the number to check if prime or not for ex 13"
      }
      },
    required: ["num"]
  }
}


// {
//   name: "getCryptoPrice",
//   args: {coin: "bitcoin"}
// }

const cryptoDeclaration = {
  name: "getCryptoPrice",
  description: "Get ithe current price of any cryptocurrency like bitcoin",
  parameters: {
    type: "OBJECT",
    properties: {
      coin: {
        type: "STRING",
        description: "It will be the crypto currenct name like bitcoin "
      }
      },
    required: ["coin"]
  }
}


const availableTools = {
  sum: sum, 
  prime: prime,
  getCryptoPrice: getCryptoPrice
}

 async function runAgent(userProblem){

  History.push({
    role: "user",
    parts: [{text: userProblem}]
  })
   
  while(true){
  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash",
    contents: History,
    config: {
      systemInstruction: "You are an AI Agent, You have access of 3 available tools to find sum of 2 number, get crypto pice of any currency and find if a number is prime or not  . use these tools whenever required to confirm user query. if user ask general question you can answer it directly if you don't need help of these three tools.",
      tools: [{
        functionDeclarations: [sumDeclaration, primeDeclaration, cryptoDeclaration]
      }]
    }
  })

  if(response.functionCalls && response.functionCalls.length > 0){
      
    const {name, args} = response.functionCalls[0];

    const funCall = availableTools[name];
    const result = await funCall(args);

    const functionResponsePart = {
      name: name, 
      response: {
        result: result
      }
    };

    //model
    History.push({
      role: "model",
      parts: [
        {
          functionCall : response.functionCalls[0],
        },
      ],
    }); 

    //result ka history daalna
      History.push({
      role: "user",
      parts: [
        {
          functionResponse: functionResponsePart,
        },
      ],
    });
  }

  else{
  History.push({
    role: "model",
    parts: [{text: response.text}]
   })
   console.log(response.text);
  }
 }
}


 async function main() {
  const userProblem = readlineSync.question("Ask me anything: ")
  await runAgent(userProblem);
  main()
 }

 main()


