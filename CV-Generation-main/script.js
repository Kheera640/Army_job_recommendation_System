// alert("Loading");
function addNewWEField() {
  //console. Log("Adding new field");

  let newNode = document.createElement ("textarea");
  newNode.classList.add ("form-control");
  newNode.classList.add ("weField");
  newNode.classList.add ("mt-2");
  newNode.setAttribute("rows", 3);
  newNode.setAttribute("placeholder", "Enter here");
 
  let weob = document.getElementById ("we") ;
  let weAddButtonOb = document.getElementById("weAddButton");
 
  weob.insertBefore(newNode, weAddButtonOb);
}

function addNewAQField() {
  let newNode = document.createElement ("textarea");
  newNode.classList.add ("form-control");
  newNode.classList.add("aqField");
  newNode.classList.add ("mt-2");
  newNode.setAttribute("rows", 3);
  newNode.setAttribute("placeholder", "Enter here");
 
  let aqob = document.getElementById ("aq") ;
  let aqAddButtonOb = document.getElementById("aqAddButton");
 
  aqob.insertBefore(newNode, aqAddButtonOb);
}  

//generating cv
function generateCV() {
  // console.log("generating CV");

   let nameField=document.getElementById('nameField').value;

   let nameT1=document.getElementById('nameT1')

   nameT1.innerHTML= nameField;

   document.getElementById("rankT").innerHTML = document.getElementById("rankField").value;
   document.getElementById("durationT").innerHTML = document.getElementById("durationField").value;

   //direct

   //contact
   document.getElementById("contactT").innerHTML = document.getElementById("contactField").value;

   //address
   document.getElementById("addressT").innerHTML = document.getElementById("addressField").value;

   //intrest
   document.getElementById('intrestT').innerHTML = document.getElementById('intrestField').value;

   //linkedin
   document.getElementById("linkedT").innerHTML = document.getElementById("linkedField").value;

    //we

    let wes=document.getElementsByClassName("weField")

    let str=""

    for(let e of wes)
    {
        str += `<li>${e.value}</li>`;
    }

    document.getElementById("weT").innerHTML=str

    //aq

   let aqs = document.getElementsByClassName("aqField");
   let str1 = "";
   for (let e of aqs) {
    str1 += `<li>${e.value}</li>`;   
   }

    document.getElementById("aqT").innerHTML = str1;

    //code for setting image

    let file=document.getElementById("imgField").files[0];

    if (file) {

    let reader = new FileReader();

    reader.readAsDataURL(file);

    //set the image to template

    reader.onloadend = function () {
      document.getElementById("imgtemplate").src = reader.result;
    };
  }

  document.getElementById("cv-form").style.display="none";
  document.getElementById("cv-template").style.display = "block";

}

 // print CV
 function printCV() {
    window.print();
  }

 function downloadCV() {
  const element = document.getElementById("cv-template");

  const opt = {
    margin:       0.5,
    filename:     "My_Resume.pdf",
    image:        { type: "jpeg", quality: 0.98 },
    html2canvas:  { scale: 2 },
    jsPDF:        { unit: "in", format: "letter", orientation: "portrait" }
  };

  document.getElementById("cv-form").style.display = "none";
  document.getElementById("cv-template").style.display = "block";

  html2pdf().set(opt).from(element).save();
}
