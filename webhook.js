const express = require('express')
const bodyparser = require('body-parser')
const axios = require('axios')
const moment = require('moment')

const app = express().use(bodyparser.json())

const token = "" //sending the request
const mytoken = "pleasework"//verifying the webhook
const flaskUrl = "http://127.0.0.1:5000/user_store" //flask server URL

app.listen(8000, () => {
    console.log('webhook is listening on port 8000')
});

app.get('/', ( req, res) => {
    res.status(200).send("The webhook is working.");
});

app.get('/webhook', (req, res) => {
    let mode = req.query["hub.mode"];
    let challenge = req.query["hub.challenge"];
    let token = req.query["hub.verify_token"];

    if(mode && token){
        if(mode === "subscribe" && token === mytoken){
            res.status(200).send(challenge);
        }else{
            res.status(403);  
        }
    }
});

const recentMessages = new Set();

app.post("/webhook",(req,res)=>{
	console.log(req) 
    let body_param=req.body;
    if(body_param.object){
        if(body_param.entry &&
            body_param.entry[0].changes &&
            body_param.entry[0].changes[0].value &&
            body_param.entry[0].changes[0].value.messages &&
            body_param.entry[0].changes[0].value.messages[0] 
            ){
               let phone_no_id=body_param.entry[0].changes[0].value.metadata.phone_number_id;
               let from = body_param.entry[0].changes[0].value.messages[0].from; 
               let msg_body = body_param.entry[0].changes[0].value.messages[0].text.body;
               let messageId = body_param.entry[0].changes[0].value.messages[0].id;

               if (!recentMessages.has(messageId)) {
                recentMessages.add(messageId); 

                console.log("=====LOGS=====");
                console.log("Phone number: " + phone_no_id);
                console.log("From: " + from);
                console.log("Message body: " + msg_body);
                console.log("=====LOGS=====");

                axios.post(flaskUrl, body_param)
                .then(response => {
                    let flaskResponse = response;
                    console.log(flaskResponse);
                })
                .catch(error => {
                    console.error("Error communicating with Flask or sending message:", error);
                });

                res.sendStatus(200); 
            } else {
                console.log("Message already processed; ignoring.");
                res.sendStatus(200); 
            }
        }
        else {
            console.log("Received a status update, not a new message.");
            res.sendStatus(200);
        }
    } else {
        console.log("Not a valid WhatsApp webhook event.");
        res.sendStatus(400);
    }
});

