
const customName = document.getElementById('customname');
const randomize = document.querySelector('.randomize');
const story = document.querySelector('.story');
const name = customName.value;

document.addEventListener('DOMContentLoaded' , function() {
  let storyText;
  let insertX;
  let insertY;
  let insertZ;

  if (document.getElementById("english").checked) {
    storyText = "In a rainforest, :insertX: entered an old palace. There, they found a magic wand. As soon as they touched it, they :insertZ:. Bob watched in amazement. Then :insertX: turned into a bird and flew away.";
    insertX = ["Aditya", "Anu", "Sudheer"];
    insertY = ["magic wand", "time machine", "invisibility cloak"];
    insertZ = ["started flying", "turned into a tree", "started singing a song"];
  } else {
    storyText = `ഒരു മഴക്കാടിൽ, <span class="other">:insertX:</span> ഒരു പഴയ കൊട്ടാരത്തിലേക്ക് കടന്നു. അവിടെ വച്ച് അവർ ഒരു മാന്ത്രിക വടി കണ്ടെത്തി. അത് പിടിച്ചതും, അവർ <span class="other">:insertZ:</span> ചെയ്തു. <span class="name">ബോബ്</span> അത്ഭുതത്തോടെ നോക്കി നിന്നു. അപ്പോൾ <span class="other">:insertX:</span> ഒരു പക്ഷിയായി മാറി ആകാശത്തേക്ക് പറന്നുപോയി.`;
    insertX = ["ആദിത്യൻ", "അനു", "സുധീർ"];
    insertY = ["മാന്ത്രിക വടി", "സമയ യാത്രാ മെഷീൻ", "അദൃശ്യതാ തൊപ്പി"];
    insertZ = ["പറക്കാൻ തുടങ്ങി", "ഒരു മരമായി മാറി", "ഒരു പാട്ട് പാടാൻ തുടങ്ങി"];
  }

  // Additional logic to process storyText and replace placeholders with actual values
  function randomValueFromArray(array){
    const random = Math.floor(Math.random()*array.length);
    return array[random];
  }
  
  customName.addEventListener('keydown', function(event){
    if (event.key === 'Enter' ){
      result();
    }
  })
  randomize.addEventListener('click', result);
  
  function result() {
  
      let newStory = storyText;
  
      const xItem= randomValueFromArray(insertX);
      const yItem= randomValueFromArray(insertY);
      const zItem= randomValueFromArray(insertZ);
  
      newStory=newStory
      newStory=newStory
      .replaceAll(":insertX:",xItem)
      .replace(":insertY:",yItem)
      .replace(":insertZ:",zItem);
    if(customName.value !== '') {
      const name = customName.value;
      newStory=newStory.replace("Bob",name).replace("ബോബ്",name);
    }
  
  
    story.innerHTML = newStory;
    story.style.visibility = 'visible';
};

});




