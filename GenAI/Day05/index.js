import { GoogleGenAI } from '@google/genai';
import readlineSync from 'readline-sync';
import { exec } from 'child_process';
import { promisify } from 'util';
import os from 'os';
import dotenv from 'dotenv';
dotenv.config(); // Load environment variables from .env file

const platform = os.platform();

const asyncExecute = promisify(exec); // Promisify exec to use async/await

const History = []
const ai = new GoogleGenAI({apiKey: process.env.GEMINI_API_KEY});


console.log("API Key:", process.env.GEMINI_API_KEY);




// Tool create krte hai , jo kisi bhi termainal.shell command ko run karne ka kaam karega

async function executeCommand({command}) {
   try {
    const {stdout, stderr} =await asyncExecute(command);

    if(stderr){
      return `Error: ${stderr}`;
    }
   return `Success: ${stdout} || TAsk executed completely`;

  } catch (error) {
     
    return `Error: ${error}`
   }
}

 const executeCommandDeclaration = {
  name: "executeCommand",
  description: "Executes a single terminal command. A command can be to create a folder, file,write on a file, edit the file or delete the file ",
  parameters: {
    type: "OBJECT",
    properties: {
      command: {
        type: "STRING",
        description: "It will be a single terminal command. Ex: mkdir calculator"
      }
    },
    required: ["command"]
  }

 }



const availableTools = {
 executeCommand
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
      systemInstruction: `You are an Website builder expert. You have to create the frontend of the website by analysing the user query. You have access of tool, which can run or execute any shell or terminal command. You can use this tool to create a folder, file, write on a file, edit the file or delete the file. You can also use this tool to run any command which is related to website building. You have to use the tool only when you are sure that you need to run a command to complete the task. If you are not sure about the command, then just reply with your thought process.

      Current user operation system is : ${platform}.
      Give command to the user according to its operating system support. For example, if the user is on Windows, then give command which is supported by Windows. If the user is on Linux, then give command which is supported by Linux. If the user is on Mac, then give command which is supported by Mac.

      <== What is your job ===>
        1. Analyse the user query to see what type of website they want to build. 
        2. Give them command one by one, step by step
        3. Use available tool to execute the command.

        // Now you can give them command in following below: 
        1. First create a folder with the name of the website., Ex: mkdir "calculator"
        2. Then create a file with the name of index.html in that folder.
        3. Then create a file with the name of style.css in that folder.
        4. Then create script.js 
        5. then write a code in html file then in css file then in js file.

        You have to provide the terminal or shell command to user, they will directly execute it . `,
      tools: [{
        functionDeclarations: [executeCommandDeclaration]
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
  // console.log(response.candidates?.[0]?.content?.parts?.[0]?.text || "No response text found.");


  }
 }
}


 async function main() {
  console.log("I am a cursor: let's build a website together!");

  const userProblem = readlineSync.question("Ask me anything: ")
  await runAgent(userProblem);
  main()
 }

// async function main() {
//   console.log("I am a cursor: let's build a website together!");

//   while (true) {
//     const userProblem = readlineSync.question("Ask me anything: ");
    
//     if (userProblem.toLowerCase() === "exit" || userProblem.toLowerCase() === "quit") {
//       console.log("Bye! Happy coding.");
//       break;
//     }

//     await runAgent(userProblem);
//     main();
//   }
// }


 main();


