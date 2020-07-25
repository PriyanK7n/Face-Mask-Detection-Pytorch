#Importing libraries
from facenet_pytorch import MTCNN
import cv2 as cv
from PIL import Image
import torch
from math import ceil as r 

#Importing modules
from CNN import ResNet15, ResNet9
from DataPreprocessing import Preprocessing

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

#model
model = ResNet15(1,2).to(device)
#model = ResNet15(1,2)

state_dict = torch.load('state_dict_resnet15.pth', map_location=device)
#loading the state_dict to the model
model.load_state_dict(state_dict)

#the classifier
mtcnn = MTCNN(select_largest=False, device=device)

# Load a single image and display
cap = cv.VideoCapture(0)

labels = {
    0:'with mask',
    1:'without mask'
    }
color_dict={
    0:(255,0,255),
    1:(255,0,0)
    }

def resize(frame, height, width):
    '''
    This function will resize the image 
    if the frame is above a certain condition
    '''
    if height and width >= 1000:
        return cv.resize(frame, (r(height*0.5), r(width*0.5)))
    elif height and width >= 2500:
        return cv.resize(frame, (r(height*0.7), r(width*0.7)))
    else:
        return cv.resize(frame, (height, width))

while True:
    success, frame = cap.read()
    
    if success:
        width, height, _ = frame.shape
        # if the video is too big uncomment the below code
        #frame = resize(frame, height, width)
        
        #padding the image to avoid the bounding going out of the image
        #and crashes the program
        padding =  cv.copyMakeBorder(frame, 50,50,50,50, cv.BORDER_CONSTANT)
        #converting numpy array into image
        image = Image.fromarray(padding)
        
        #gives the face co-ordinates
        face_coord,_ = mtcnn.detect(image)
        
        
        if face_coord is not None:
            for coord in face_coord:
                for x1,y1,x2,y2 in [coord]:
                    x1,y1,x2,y2 = r(x1),r(y1),r(x2),r(y2)
                    
                    #face array
                    face = padding[y1:y2 ,x1:x2]
                    
                    #Preprocessing
                    preprocess = Preprocessing(img=Image.fromarray(face))
                    #tensor array
                    tensor_img_array = preprocess.preprocessed_arrays()
                    
                    #Predicting
                    prob, label = torch.max(torch.exp(model(
                                            tensor_img_array.to(device))),dim=1)
                    
                    scale = round((y2-y1)*35/100)
                    #mini box
                    cv.rectangle(frame, (x1-50,y1-50), (x1-40,y1-40), 
                                                    color_dict[label.item()],-1)

                    #Bounding box
                    cv.rectangle(frame, (x1-50,y1-50), (x2-50,y2-50), 
                                                    color_dict[label.item()],1)
            
                    cv.putText(frame,labels[label.item()], 
                                (x1-50,y1-53),cv.FONT_HERSHEY_SIMPLEX,
                                                        scale*0.01,(255,255,0),1)
                    
        cv.imshow("Frame", frame)
        # im = Image.fromarray(frame)
        # im.save('mask/a%s.png'%(a))
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

         
    else:
        print('End')
        break
    
cap.release()
cv.destroyAllWindows()

