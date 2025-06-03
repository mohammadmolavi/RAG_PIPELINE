// window.onload = function () {
//   fetch("/headings")
//     .then(res => res.json())
//     .then(data => {
//       populateDropdown("heading1", data.heading1);
//       populateDropdown("heading2", data.heading2);
//     });
// };

     

// function populateDropdown(id, items) {
//   const dropdown = document.getElementById(id);
//   dropdown.innerHTML = `<option value="">-- Select ${id} --</option>`;
//   items.forEach(item => {
//     const opt = document.createElement("option");
//     opt.value = item;
//     opt.textContent = item;
//     dropdown.appendChild(opt);
//   });
// }

// function submitQuery() {
//   const query = document.getElementById("query").value;
//   const heading1 = document.getElementById("heading1").value;
//   const heading2 = document.getElementById("heading2").value;
//     if (!isValidQuestion(query)) {
//       alert("Please enter a valid question.");
//       return;
//     }
//     else{const payload = {
//     query: query,
//     heading1: heading1 || null,
//     heading2: heading2 || null
//   };

//   fetch("/retrieve", {
//     method: "POST",
//     headers: { "Content-Type": "application/json" },
//     body: JSON.stringify(payload)
//   })
//     .then(res => res.json())
//     .then(data => {
//       const chunks = data.results || data; // بسته به خروجی
//       const resultDiv = document.getElementById("result");
//       resultDiv.innerHTML = "<h3>Retrieved Chunks:</h3>";

//       // نمایش تمام chunkها
//       chunks.forEach((chunk, index) => {
//         const chunkDiv = document.createElement("div");
//         chunkDiv.classList.add("chunk");
//         chunkDiv.innerHTML = `
//           <p><strong>Chunk ${index + 1}</strong></p>
//           <p><strong>Heading 1:</strong> ${chunk.payload["heading 1"]}</p>
//           <p><strong>Heading 2:</strong> ${chunk.payload["heading 2"]}</p>
//           <p><strong>Similarity:</strong> ${chunk.score.toFixed(3)}</p>
//           <p><strong>Text:</strong> ${chunk.payload.text}</p>
//           <hr/>
//         `;
//         resultDiv.appendChild(chunkDiv);
//       });

//       if (chunks.length > 0) {
//         const generatePayload = {
//           query: query,
//           context: chunks[0].payload.text
//         };

//         // ارسال فقط اولین chunk به /generate
//         return fetch("/generate", {
//           method: "POST",
//           headers: { "Content-Type": "application/json" },
//           body: JSON.stringify(generatePayload)
//         });
//       } else {
//         throw new Error("No chunks retrieved.");
//       }
//     })
//     .then(res => res.json())
//     .then(gen => {
//       // افزودن پاسخ نهایی
//       const resultDiv = document.getElementById("result");
//       const answerDiv = document.createElement("div");
//       answerDiv.innerHTML = `<h3>Generated Answer:</h3><p>${gen.answer}</p>`;
//       resultDiv.appendChild(answerDiv);
//     })
//     .catch(err => {
//       document.getElementById("result").innerHTML = `<p style="color:red;">Error: ${err.message}</p>`;
//     });}
  
// }



      // Retrieve chunks
    //   const retrieveRes = await fetch("/retrieve", {
    //     method: "POST",
    //     headers: { "Content-Type": "application/json" },
    //     body: JSON.stringify(payload)
    //   });
   // .then(response => response.json())
    // .then(data => {
    //   document.getElementById("result").textContent = JSON.stringify(data, null, 2);
    // })
    // .catch(error => {
    //   document.getElementById("result").textContent = "Error: " + error;
    // });}
    //   print("salam");
    //   print()

 function isValidQuestion(question) {
      question = question.trim();

      if (question.length < 8) return false;

      const questionWords = [
    "what", "why", "how", "when", "where", "who", "is", "are", "do", "does", "can", "should", "could"
      ];

    const startsWithQuestionWord = questionWords.some(word =>
    question.toLowerCase().startsWith(word)
    );
    const endsWithQuestionMark = /[؟?]\s*$/.test(question);
    const hasLetters = /[a-zA-Z]/.test(question);

  return (startsWithQuestionWord || endsWithQuestionMark) && hasLetters;
}





   async function ask() {
      const question = document.getElementById("question").value;
      const heading_1 = document.getElementById("heading_1").value;
      const heading_2 = document.getElementById("heading_2").value;
      const json_payload = {
    query: question,
    heading_1: heading_1 || null,
    heading_2: heading_2 || null
  };



    if (!isValidQuestion(question)) {
        alert("Please enter a valid question.");
        return;
      }
    else{

    document.getElementById("chunks").innerHTML = "Loading...";
    document.getElementById("answer").innerText = "";
    const retrieveRes = await fetch("/retrieve", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(json_payload)
  })
 
    const retrieveData = await retrieveRes.json();

    //   const retrieveData = submitQuery();
      const chunksDiv = document.getElementById("chunks");
      chunksDiv.innerHTML = "";
      retrieveData.documents.forEach(doc => {
      const payload = doc.payload;
      const score = doc.score;
      const div = document.createElement("div");
      div.className = "chunk";
      div.innerHTML = `
        <b>Heading_1:</b> ${payload["heading_1"]}<br>
        <b>Heading_2:</b> ${payload["heading_2"]}<br>
        <b>Score:</b> ${score.toFixed(3)}<br>
        <b>Text:</b> ${payload.text}
      `;
      chunksDiv.appendChild(div);
    });
        const chunk_1 = retrieveData.documents[0];
        const chunk_2 = retrieveData.documents[1] || "";
        const chunk_3 = retrieveData.documents[2] || "";


        const chunk_1_text = chunk_1?.payload?.text || "";
        const chunk_2_text = chunk_2?.payload?.text || "";
        const chunk_3_text = chunk_3?.payload?.text || "";
        // Generate answer
        const generateRes = await fetch("/generate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
              question: question,
              chunk_1: chunk_1_text,
              chunk_2: chunk_2_text,
              chunk_3:chunk_3_text,})
        });
        const generateData = await generateRes.json();
        document.getElementById("answer").innerText = generateData.answer;
      }}