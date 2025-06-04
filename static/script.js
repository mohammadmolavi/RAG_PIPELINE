
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
    if(!retrieveData.documents || retrieveData.documents.length === 0) {
      document.getElementById("chunks").innerHTML = "No relevant chunks found.";
      return;
    }                                  
    else{const chunksDiv = document.getElementById("chunks");
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
        document.getElementById("answer").innerText = generateData.answer;}

    //   const retrieveData = submitQuery();
      
      }}