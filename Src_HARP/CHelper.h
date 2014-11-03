// (c) 2014 Dominic Springer
// File licensed under GNU GPL (see HARP_License.txt)

#pragma once
#include <unistd.h>
#include <iostream>
#include <iomanip>
#include <typeinfo>
#include <vector>

#include <vector>
#include <opencv/cv.hpp>
#include <opencv2/core/core.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/features2d/features2d.hpp>

//#include <boost/foreach.hpp>
//#include <boost/tokenizer.hpp>
//#include "OpenEXR/half.h"
#include <QString>
#include <QProcess>
#include "HARP_Defines.h"

using namespace std;
using namespace cv;
//using namespace boost;

inline bool doesFileExist(string FN)
{
    std::ifstream infile(FN.c_str());
    return infile.good();
}

inline void sleepFor(float seconds)
{
	unsigned int microseconds = (unsigned int) seconds*1000*1000;
	usleep(microseconds);
}

Mat invertImage(Mat Image);
void convertToCV_8UC3(Mat &Image);

//------------------------------------------------------------------
// writeJPG
//------------------------------------------------------------------
enum ENumerationType
{
	NO_ENUM, AUTO_ENUM, MANUAL_ENUM
};
//inline void writeJPG(Mat image, string Identifier, ENumerationType NumerationType = AUTO_ENUM, int ManualNumber = 1000)
//{
//	if(SKIP_JPEGS)
//	  return;
//
//	//const char *Format = "jpg";
//	const char *Format = "png";
//
//	if(IS_INVERTING)
//		image = invertImage(image);
//
//	system("mkdir -p ./images");
//	int Quality = JPG_QUALITY; //100 = best
//	vector<int> params;
//	params.push_back(CV_IMWRITE_JPEG_QUALITY);
//	params.push_back(Quality);
//	char outjpg[100];
//	static int AutoNumber = 0;
//	if (NumerationType == NO_ENUM)
//	{
//		sprintf(outjpg, "images/%s.%s", Identifier.c_str(), Format);
//	}
//	else if (NumerationType == AUTO_ENUM)
//	{
//		sprintf(outjpg, "images/%s_%.4d.%s", Identifier.c_str(), AutoNumber, Format);
//		AutoNumber++;
//	}
//	else // MANUAL NUMBER
//	{
//		sprintf(outjpg, "images/%s_%.4d.%s", Identifier.c_str(), ManualNumber, Format);
//	}
//
//	cout << "Wrote: " << outjpg << endl;
//	imwrite(outjpg, image, params);
//}

inline void writeJPG_Direkt(Mat image, string FileName)
{
//  if(SKIP_JPEGS)
//    return;

  //format given by provided filename!
  int Quality = JPG_QUALITY; //100 = best
  vector<int> params;
  params.push_back(CV_IMWRITE_JPEG_QUALITY);
  params.push_back(Quality);

  //INVERTING
  if (IS_INVERTING)
    image = invertImage(image);

#ifdef JPG_DIMX
  float Ratio = float(JPG_DIMX)/image.cols;
  int JPEG_DimY = int(Ratio*image.rows);
  cv::resize(image, image, cv::Size2i(JPG_DIMX, JPEG_DimY));
#endif

  imwrite(FileName, image, params);
  cout << "Wrote: " << FileName << endl;

}

inline void resizeToHeight(Mat &Img, int Height)
{
  float RatioY = float(Img.rows)/Height;
  int Width = int(Img.cols/RatioY);
  resize(Img, Img, cv::Size2i(Width, Height), 0, 0, INTER_NEAREST);
}

inline void resizeToWidth(Mat &Img, int Width)
{
  float RatioX = float(Img.cols)/Width;
  int Height = int(Img.rows/RatioX);
  resize(Img, Img, cv::Size2i(Width, Height), 0, 0, INTER_NEAREST);
}

inline void padToWidth(Mat &Img, int Width)
{
  int CurWidth = Img.cols;
  Mat Pad = Mat(Img.rows,Width-CurWidth, CV_8UC3, WHITE);
  hconcat(Img, Pad, Img);
}

//------------------------------------------------------------------
// writeText
//------------------------------------------------------------------
inline void writeText(Mat Matrix, QString text, Scalar color = Scalar(0, 0, 0), Point textOrg = Point(3, 3.0), double fontScale = 1.0, int thickness = 2)
{
	//int fontFace = FONT_HERSHEY_SIMPLEX;
	int fontFace = FONT_HERSHEY_PLAIN;

	int baseline = 0;
	//Size textSize = getTextSize(text, fontFace, fontScale, thickness, &baseline);
	baseline += thickness;

	 //RegEx for ' ' or ',' or '.' or ':' or '\t': QRegExp rx("(\\ |\\,|\\.|\\:|\\t)");
	QRegExp rx("(\\n)");
	QStringList query = text.split(rx);

  foreach (QString textrow,query) //C++11 feature man!
	{
    textOrg.y += 20*fontScale;
    putText(Matrix, textrow.toLocal8Bit().constData(), textOrg, fontFace, fontScale, color, thickness, 3);
  }
}

inline void writeText(Mat Matrix, QString text, double fontScale = 1.0, Scalar color = Scalar(0, 0, 0), Point textOrg = Point(3, 3.0), int thickness = 2)
{
  writeText(Matrix, text, color, textOrg, fontScale, thickness);
}

//------------------------------------------------------------------
// convert YCrCb to RGB, return copy
//------------------------------------------------------------------
inline Mat getRGB(Mat &YCrCb)
{
	Mat RGB;
	cv::cvtColor(YCrCb, RGB, CV_YCrCb2RGB);
	return RGB;
}

inline Mat getRGB(Mat &Y, Mat &U, Mat &V)
{
	Mat YUV;
	Mat pointers[] =
	{ Y, U, V };
	merge(pointers, 3, YUV); //now its RGB!

	Mat RGB;
	cv::cvtColor(YUV, RGB, CV_YCrCb2RGB);
	return RGB;
}

inline void convertToCV_8UC3(Mat &Image)
{
	if (Image.channels() != 3) //grayscale to color
	{
		Mat tmp;
		Mat pointers[] =
		{ Image, Image, Image };
		merge(pointers, 3, tmp); //now its RGB!
		Image = tmp.clone();
	}

	if (Image.depth() != CV_8U)
		Image.convertTo(Image, CV_8U);
}

//------------------------------------------------------------------
// invertImage
//------------------------------------------------------------------
inline Mat invertImage(Mat Image)
{
	Mat cloned = Image.clone();
	cloned.convertTo(Image, CV_8U);

	Mat inverted = cloned.clone(); //reserving space
	inverted = Scalar(255, 255, 255);
	inverted -= cloned;
	return inverted;
}

//------------------------------------------------------------------
// getMatrixType
//------------------------------------------------------------------
inline void getMatrixType(cv::Mat M, const char* string)
{
	if (string != NULL)
		std::cout << "----Type of matrix " << string << "----" << endl;
	else
		std::cout << "----Type of matrix ----" << endl;

	cv::Size sizeM = M.size();
	int rows = sizeM.height;
	int cols = sizeM.width;
	int depth = M.depth();
	char depthstr[50];
	switch (depth)
	{
	case CV_8U:
		sprintf(depthstr, "CV_8U");
		break;
	case CV_8S:
		sprintf(depthstr, "CV_8S");
		break;
	case CV_16U:
		sprintf(depthstr, "CV_16U");
		break;
	case CV_16S:
		sprintf(depthstr, "CV_16S");
		break;
	case CV_32S:
		sprintf(depthstr, "CV_32S");
		break;
	case CV_32F:
		sprintf(depthstr, "CV_32F");
		break;
	case CV_64F:
		sprintf(depthstr, "CV_64F");
		break;
	default:
		sprintf(depthstr, "USERTYPE");
		break;
	}

	cout << "Cols x Rows = " << cols << "x" << rows << ", ";
	cout << "Type = " << depthstr << ", Dims = " << M.dims << ", NumChannels = " << M.channels() << "\n";
}

//------------------------------------------------------------------
// printMatrix
//------------------------------------------------------------------
inline void printMatrix(cv::Mat M, const char* string)
{
	stringstream sout(stringstream::in | stringstream::out);
	cv::Size sizeM = M.size();
	int rows = sizeM.height;
	int cols = sizeM.width;

	if (string != NULL)
		sout << "----Matrix " << string << "----" << endl;
	else
		sout << "----Matrix ----" << endl;

	//getMatrixType(M, string);
	sout << setw(5) << fixed; // << setprecision( 3 );// << right << fixed;

	if (M.channels() == 1) //2D matrix, like H or F
	{
		for (int row = 0; row < rows; ++row)
		{
			for (int col = 0; col < cols; ++col)
			{
				if (M.depth() == 6)
					sout << (double) M.at<double>(row, col) << " ";
				else if (M.depth() == 5)
					sout << (double) M.at<float>(row, col) << " ";
				else
					assert(0);
			}
			sout << endl;
		}
		sout << flush;
	}
	else //uh oh, some strange 3D points matrix, originating from vector<Point2f> (OpenCV likes those!)
	{
		//indexing separate channels is tough!
		vector<Mat> splitted;
		split(M, splitted);
		for (int ch = 0; ch < M.channels(); ch++)
		{
			sout << "--------Channel " << ch << ": ----------" << endl;
			for (int row = 0; row < rows; ++row)
			{
				for (int col = 0; col < cols; ++col)
				{
					if (col > 100)
						continue;

					if (M.depth() == 6)
						sout << (double) splitted[ch].at<double>(row, col) << " ";
					else if (M.depth() == 5)
						sout << (double) splitted[ch].at<float>(row, col) << " ";
					else
						assert(0);
					sout << "\t";
				}

			}
			sout << endl;
		}
		sout << flush;
	}

	cout << sout.str();
	//return sout.str();
}

//------------------------------------------------------------------
// CYuvReader
//------------------------------------------------------------------
class CYuvReader
{
public:

  CYuvReader(const char *file, unsigned short w, unsigned short h)
  {
    width = w;
    height = h;
    pSourcefile = fopen(file, "rb");

    if(pSourcefile == NULL)
    {
      cout << "Couldn't open file " << file << endl;
      endOfFile = 0;
    }
    else
    {
      fseek(pSourcefile, 0, SEEK_END);
      endOfFile = ftell(pSourcefile);
      fseek(pSourcefile, 0, SEEK_SET);
    }
  }

  Mat getMatY()
  {
    if(pSourcefile == NULL)
      return Mat();

    int pos = ftell(pSourcefile);
    assert(pos < endOfFile);
    unsigned char *samples = new unsigned char[width*height];
    int length = fread(samples, sizeof(unsigned char), width*height, pSourcefile);
    assert(length==width*height);
    Mat tmp = Mat(height, width, CV_8UC1,samples);
    Mat M = tmp.clone();
    fseek(pSourcefile, width*height/2, SEEK_CUR);
    delete[] samples;
    return M;
  }

  void getMatYUV444(Mat &Y, Mat &U, Mat &V, int DimX, int DimY)
  {
    if(pSourcefile == NULL)
      assert(0);
    int pos = ftell(pSourcefile);
    assert(pos < endOfFile);

    unsigned char *y = (unsigned char*) malloc (DimX*DimY);
    unsigned char *u = (unsigned char*) malloc (DimX*DimY/4);
    unsigned char *v = (unsigned char*) malloc (DimX*DimY/4);

      fread(y, sizeof(unsigned char), width*height, pSourcefile);
      fread(u, sizeof(unsigned char), width*height/4, pSourcefile);
      fread(v, sizeof(unsigned char), width*height/4, pSourcefile);

      Mat tmp;
      tmp = Mat(height, width, CV_8UC1,y);
      Y = tmp.clone();
      tmp = Mat(height/2, width/2, CV_8UC1,u);
      cv::resize(tmp, U, Size(width, height));
      tmp = Mat(height/2, width/2, CV_8UC1,v);
      cv::resize(tmp, V, Size(width, height));

      delete[] y;
      delete[] u;
      delete[] v;
  }

  void getMatYUV420(Mat &Y, Mat &U, Mat &V, int DimX, int DimY)
  {
    if(pSourcefile == NULL)
      assert(0);
    int pos = ftell(pSourcefile);
    assert(pos < endOfFile);

    unsigned char *y = (unsigned char*) malloc (DimX*DimY);
    unsigned char *u = (unsigned char*) malloc (DimX*DimY/4);
    unsigned char *v = (unsigned char*) malloc (DimX*DimY/4);

    int BytesRead[3];
    BytesRead[0] = fread(y, sizeof(unsigned char), width*height, pSourcefile);
    BytesRead[1] = fread(u, sizeof(unsigned char), width*height/4, pSourcefile);
    BytesRead[2] = fread(v, sizeof(unsigned char), width*height/4, pSourcefile);

    if(BytesRead[0] != width*height || BytesRead[1] != width*height/4 || BytesRead[2] != width*height/4) //ERROR!
    {
      cout << "ERROR: " << BytesRead[0] << " " << BytesRead[1] << " " << BytesRead[2] << endl;
      assert(0);
    }

      Mat tmp;
      tmp = Mat(height, width, CV_8UC1,y);
      Y = tmp.clone();
      tmp = Mat(height/2, width/2, CV_8UC1,u);
      U = tmp.clone();
      tmp = Mat(height/2, width/2, CV_8UC1,v);
      V = tmp.clone();

      delete[] y;
      delete[] u;
      delete[] v;
  }

  int getNumFrames()
  {
    return endOfFile/(width*height*1.5);
  }

  void skipFrames(int SkipFrames)
  {
    fseek(pSourcefile, SkipFrames*width*height*1.5, SEEK_SET);
  }



  unsigned int endOfFile;
  unsigned short height;
  unsigned short width;
  FILE *pSourcefile;
};

//------------------------------------------------------------------
// Img Matrix
//------------------------------------------------------------------
class CImgMatrix
{
  //TODO: Change Rows to CurRow
  //TODO: Find a solution for last row problem

public:
  int Rows, Cols, RowHeight, MaxRows, RowsPerImg;
  int CurCol;
  int LabelHeight; //pixel height of label stripes (for a row and all Mats in this row)
  vector<vector<Mat> > Matrix;
  vector<vector<QString> > LabelMatrix;
  vector<Scalar> RowColorList;
  QStringList RowLabelList;

  CImgMatrix()
  {
    Rows = 0;
    CurCol = 0;
    Cols = -1; //set by owner


    RowHeight = 64*4; //EVERY entry in the row is scaled to this height individually
    MaxRows = 100;//1000; //limit Final to 30 rows
    RowsPerImg = 50; //rows written to one jpg
    LabelHeight = 40;
  }

  void reset()
  {
    for(int r=0; r<Rows; r++)
    {
      Matrix[r].clear();
      LabelMatrix[r].clear();
    }
    Matrix.clear();
    LabelMatrix.clear();
    RowLabelList.clear();
    RowColorList.clear();
    Rows = 0;
    CurCol = 0;
  }

//  void setImg(int Col, Mat Img, QString Info) //always sets in last row
//  {
//    //------------------------------------------
//    //HACK TO SAVE MEMORY FOR FULL OUTPUT
//    //------------------------------------------
//    if(Col == 3 || Col == 5 || Col == 7)
//      return;
//
//    if(Rows == MaxRows) //we are at the end and over the last image
//      putText(Img, "LAST", Point(0.0, 20), FONT_HERSHEY_PLAIN, 1.0, RED, 2, 3);
//
//    LabelMatrix[Rows-1][Col] = Info;
//    Matrix[Rows-1][Col] = Img;
//  }

  void pushImg(Mat Img, QString Info) //always sets in last row
  {
    if(Rows == MaxRows) //we are at the end and over the last image
      putText(Img, "LAST", Point(0.0, 20), FONT_HERSHEY_PLAIN, 1.0, RED, 2, 3);

    if(CurCol == Cols-1) //All bad things must come to an end, Jesse
    {
      cout << "Warning CImgMatrix: to less columns, image lost" << endl;
      return;
    }

    LabelMatrix[Rows-1][CurCol] = Info;
    Matrix[Rows-1][CurCol] = Img;
    CurCol++;
  }


  void createEmptyRow(QString RowLabel, Scalar RowColor)
  {
    CurCol = 0; //carriage return
    if(Rows >= MaxRows) //All bad things must come to an end, Jesse
      return;

    RowLabelList.append(RowLabel);
    RowColorList.push_back(RowColor);

    assert(Cols != -1); //somebody forgot to initialize...

    vector<Mat> Row;
    vector<QString> LabelRow;
    for(int c=0; c<Cols; c++)
    {
      //the top label
      LabelRow.push_back(QString());

      //the image
      Mat Proxy = Mat(); //Mat(64,64, CV_8UC3, Scalar(128,128,128)); //simple 64x64 gray patch with number
      //writeText(Proxy, std::to_string(c), 2.0);
      Row.push_back(Proxy); //push_back here: append to right
    }
    Matrix.push_back(Row);
    LabelMatrix.push_back(LabelRow);
    Rows++;

  }

  Mat assembleOneRow(int r)
  {
    Mat ImgRow;

    QString HeadlineLabel = RowLabelList[r];

    for(int c=0; c<Cols; c++)
    {
      //get the img at this position
      Mat CurImg = Matrix[r][c];

      //convert to correct format (maybe just single channel, or 16 Bit, or ...)
      convertToCV_8UC3(CurImg);

      QString ColumnLabel = LabelMatrix[r][c];
      if(c == 0)
      {
        bool test = CurImg.empty();
//        assert(CurImg.empty() == false); //first Mat must never be empty
      }
      if(CurImg.empty()) //empty entries may happen (may now be obsolete with pushImg)
        continue;


      //scale image to desired height
      int ImgHeight = CurImg.rows;
      resizeToHeight(CurImg, RowHeight);

      //add top label
      Mat TopLabel(LabelHeight,CurImg.cols, CV_8UC3, RowColorList[r]);
      putText(TopLabel, ColumnLabel.toLocal8Bit().constData(), Point(3.0, 30), FONT_HERSHEY_PLAIN, 1.6, Scalar(0, 0, 0), 2, 3);
      vconcat(TopLabel, CurImg, CurImg);

      //inserting col-spacer
      Mat Spacer(RowHeight+LabelHeight,20, CV_8UC3, RowColorList[r]);

      if(c == 0){
        ImgRow = CurImg; //first column
        hconcat(Spacer, ImgRow, ImgRow); //left border
        hconcat(ImgRow, Spacer, ImgRow); //right border
      }
      else {
        hconcat(ImgRow, CurImg, ImgRow);
        hconcat(ImgRow, Spacer, ImgRow);
      }

      //Mat test = Matrix[r][c].t();
      //LeftImg.push_back(Matrix[r][c].t());
    }

    //inserting top v-spacer
    Mat Spacer(LabelHeight,ImgRow.cols, CV_8UC3, RowColorList[r]);
    putText(Spacer, HeadlineLabel.toLocal8Bit().constData(), Point(3.0, 30), FONT_HERSHEY_PLAIN, 2.0, Scalar(0, 0, 0), 2, 3);
    //resizeToWidth(Spacer, ImgRow.cols);
    vconcat(Spacer, ImgRow, ImgRow);

    //inserting bottom v-spacer
    Spacer = RowColorList[r];
    Spacer(Rect(0, Spacer.rows/2, Spacer.cols, Spacer.rows/2)) = WHITE;
    vconcat(ImgRow, Spacer, ImgRow);

    return ImgRow;
  }

  void saveFinal(string FN)
  {
    //cout << "ImgMatrix getFinal: " << Rows << "x" << Cols << " images" <<  endl;

    Mat Final;


    //preprocessing: compile a vector of large row-images
    //TODO: also limit to number of rows that actually are saved to PNG
    vector<Mat> VectorOfRows;
    for(int r=0; r<Rows; r++)
    {
      //ASSEMBLE ONE ROW
      Mat ImgRow = assembleOneRow(r);
      VectorOfRows.push_back(ImgRow);
      Matrix[r].clear(); //free memory, don't need those Mats any more
    }

    //if there is something to write
    if(Rows > 0)
    {
      //let us see what the maximal row width is
      int RowDimX = 0;
      int RowDimY = VectorOfRows[0].rows;
      for(int r=0; r<Rows; r++)
      {
        if (VectorOfRows[r].cols > RowDimX)
          RowDimX = VectorOfRows[r].cols;
      }

      //let us pad all rows which are too short
      for(int r=0; r<Rows; r++)
      {
        if (VectorOfRows[r].cols < RowDimX)
          padToWidth(VectorOfRows[r], RowDimX);
        assert(RowDimY == VectorOfRows[r].rows ); //all rows must be fixed in height!
      }



      //we now create a >>reduced<< Mat image for saving to file
      int NumTotalRows = (Rows < MaxRows) ? Rows : MaxRows;

      int NumRuns = int(ceil(float(NumTotalRows) / RowsPerImg));
      int cnt = 0;
      for(int run = 0; run < NumRuns; run++)
      {
        int TmpNum = (NumTotalRows < RowsPerImg) ? NumTotalRows : RowsPerImg;
        Final = Mat(TmpNum*RowDimY,RowDimX, CV_8UC3, WHITE);
        for(int r=0; r < TmpNum && cnt < NumTotalRows; r++, cnt++)
        {
          VectorOfRows[cnt].copyTo(Final(Rect(0,r*RowDimY, RowDimX, RowDimY)));
        }

        //HACK
        //resizeToWidth(Final, 1024);
        QString FN_tmp(FN.c_str());
        FN_tmp.chop(4); //chop extension
        FN_tmp.append(QString("_Part%1%2").arg(run).arg(IMAGE_FORMAT));
        writeJPG_Direkt(Final, FN_tmp.toStdString());
        //cout << "Written " << NumRows << " rows" << endl;
      }
    }
  }
};



