//Chon anh 
const getImage = (event) => {
  //set ảnh cho phần preview
  const image = document.getElementById('preview_img');
  image.src = URL.createObjectURL(event.target.files[0]);
}


//Them anh 
const addImage = (item) => {
  //Thêm ảnh vào list
  //Lấy src ảnh
  const imageList = document.getElementById('img_list');
  const src = item['img_url']
  //tạo div chứa ảnh
  const imgListItem = document.createElement('div')
  imgListItem.className = "img_list_item";

  //tạo div chứa kết quả
  const detectionRate = document.createElement('div')
  detectionRate.className = "img_list_rate"
  detectionRate.innerHTML = `${item["label"]}: ${item["dist"]}`;

  //gán src cho ảnh
  const child = document.createElement('img')
  child.className = "img_list_img"; child.src = src;

  //thêm  ảnh và kết quả vào div chứa
  imgListItem.appendChild(detectionRate);
  imgListItem.appendChild(child);

  //đưa div chứa vào đầu list
  imageList.prepend(imgListItem)

  imageList.style.overflowX = scroll;

}


//Search
const handleSearchBtn = (event) => {
  event.preventDefault();

  const imageList = document.getElementById('img_list');
  while (imageList.firstChild) {
    imageList.removeChild(imageList.lastChild);
  }

  let url = "/images/";

  var fileInput = document.getElementById("choose_file");

  if (fileInput.files.length === 0) {
    alert("Please select a file to upload.");
    return;
  }

  let formData = new FormData();         
  
  formData.append("file", fileInput.files[0]);

  fetch(url, {
      method: "POST", 
      body: formData
  }).then(data => {
      data.json().then(obj=>{
          console.log(obj)
          let process_url = obj["processed"]
          let label = obj["label"]
          let nearest = obj["nearest"]
          let score = obj["score"]

          document.getElementById("search_img").src = process_url
          document.getElementById("btn_result").innerHTML = `${label}\nRatio ${score["num"]}/${nearest.length}`
          for (let i = nearest.length-1; i >=0 ; i--){
            addImage(nearest[i])
          }
          
      })
      .catch("patser error");
  }).catch("post error");
}