#include <iostream>
#include <fstream>
#include <random>
#include <time.h>
#include <chrono>
#include <vector>


//#include <boost/numeric/ublas/io.hpp>
//#include <boost/numeric/ublas/tensor.hpp>
//#include <boost/numeric/ublas/matrix.hpp>


using namespace std;
//using namespace boost::numeric::ublas;

int DATA_NUM = 100;
int DATA_DIM = 2;
int COMPONENT_NUM = 3;

std::string FILE_NAME = "./gmm.dat";


class Gaussian_Model
{
public:
	Gaussian_Model(std::size_t dim)
	{
		dim_ = dim;
		count_ = 0;
		prior_ = 0.0f;
		mptr_ = 0;

	/*	mean_ = new float[dim];
		var_ = new float[dim * dim];*/
	}

	Gaussian_Model(std::size_t dim, float m, float s, float p)
	{
		dim_ = dim;
		count_ = 0;
		prior_ = p;
		mptr_ = 0;
	/*	mean_ = new float[dim];
		var_ = new float[dim * dim];

		int i;
		for (i = 0; i < dim; i++)
		{
			mean_[i] = m;
			var_[i + i * dim] = s;
		}*/
	}

	~Gaussian_Model()
	{
		if (mptr_)
		{
			delete[] mptr_;
			mptr_ = 0;
		}	
	}

	void init()
	{
		mptr_ = new float[dim_ + dim_ * dim_ * 2];
		mean_ = mptr_;
		var_ = mean_ + dim_ * dim_;
		invvar_ = var_ + dim_ * dim_;
	}

	float* getmean() { return mean_; };
	float* getstd() { return var_; };
	float getprior() { return prior_; };
	void setprior(float v) { prior_ = v; };
	float getcount() { return count_; };
	void setcount(float v) { count_ = v; };
	int getdim() { return dim_; };

	//mean = alpha
	void setmean(float alpha)
	{
		int i;
		for (i = 0; i < dim_; i++)
		{
			mean_[i] = alpha;
		}
	}

	//mean = mean + alpha * data
	void accumulatemean(float alpha, float* data)
	{
		int i;
		for (i = 0; i < dim_; i++)
		{
			mean_[i] += alpha * data[i];
		}
	}

	void setmean(float* data)
	{
		memcpy(mean_, data, dim_ * sizeof(float));
	}

	void scalemean(float alpha)
	{
		int i;
		for (i = 0; i < dim_; i++)
		{
			mean_[i] *= alpha;
		}
	}

	void accumulatecount(float count)
	{
		count_ += count;
	}

	void accumulatevar(float alpha, float* data)
	{
		int i, j;
		float v;
		for (i = 0; i < dim_; i++)
		{
			for (j = i; j < dim_; j++)
			{
				v = data[i] * data[j] * alpha;
				var_[i * dim_ + j] += v;
				var_[j * dim_ + i] += v;
			}
		}
	}

	void accumulatevar2(float alpha, float* data)
	{
		int i, j;
		float* temp = new float[dim_];

		for (i = 0;i < dim_; i++)
		{
			temp[i] = data[i] * alpha;
		}

		for (i = 0; i < dim_; i++)
		{
			for (j = 0; j < dim_; j++)
			{
				var_[i * dim_ + j] += temp[i] * data[j];
			}
		}

		delete[] temp;
	}

	void setvar(float alpha)
	{
		int i;
		for (i = 0; i < dim_ * dim_; i++)
		{
			var_[i] = alpha;
			invvar_[i] = 1 / alpha;
		}
	}

	void setdiagvar(float alpha)
	{
		int i;
		for (i = 0; i < dim_; i++)
		{
			var_[i + i * dim_] = alpha;
			invvar_[i + i * dim_] = 1 / alpha;
		}
	}

	void scalevar(float alpha)
	{
		int i;
		for (i = 0; i < dim_ * dim_; i++)
		{
			var_[i] *= alpha;
			invvar_[i] /= alpha;
		}
	}

	float calprob(float* data)
	{
		return 1.0f;
	};

	float calinvvar()
	{
		
	}

	void preprocess()
	{
		this->setmean(0.0f);
		this->setcount(0.0f);
		this->setvar(0.0f);
	};

	void updatestep(float prob, float* x)
	{
		this->accumulatecount(prob);
		this->accumulatemean(prob, x);
		this->accumulatevar(prob, x);
	};

	void postprocess(int N)
	{
		this->scalemean(1.0f / N);
		this->setprior(this->getcount() / N);
		this->scalevar(1.0f / N);
	}

	void printinfo()
	{
		int i, j;
		std::cout << "dim: " << dim_ << std::endl;
		std::cout << "mean: ";
		for (i = 0;i < dim_; i++)
		{
			std::cout << mean_[i] << " ";
		}
		std::cout << std::endl;

		std::cout << "prior: " << prior_ << std::endl;
		std::cout << "count: " << count_ << std::endl;

		std::cout << "var: " << std::endl;
		for (i = 0; i < dim_; i++)
		{
			for (j = 0;j < dim_; j++)
			{
				std::cout << var_[i * dim_ + j] << " ";
			}

			std::cout << std::endl;
		}

		std::cout << std::endl;
	}

private:
	float* mptr_;
	float* mean_;
	float* var_;
	float prior_;
	float count_;
	std::size_t dim_;
	float* invvar_;
};


void generatedata()
{
	unsigned seed = std::chrono::system_clock::now().time_since_epoch().count();

	std::default_random_engine generator(seed);
	std::normal_distribution<float> distribution(0.0, 1.0);

	int i, j;
	ofstream ouF;
	ouF.open(FILE_NAME, std::ofstream::binary | std::ofstream::out);
	ouF.write(reinterpret_cast<const char*>(&DATA_NUM), sizeof(DATA_NUM));
	ouF.write(reinterpret_cast<const char*>(&DATA_DIM), sizeof(DATA_DIM));

	for (i = 0; i < DATA_NUM; i++)
	{
		for (j = 0; j < DATA_DIM; j++)
		{
			float x = distribution(generator);
			ouF.write(reinterpret_cast<const char*>(&x), sizeof(float));
		}
	}

	ouF.close();
}

float* readdata()
{
	ifstream inF;
	inF.open(FILE_NAME);

	inF.read(reinterpret_cast<char*>(&DATA_NUM), sizeof(DATA_NUM));
	inF.read(reinterpret_cast<char*>(&DATA_DIM), sizeof(DATA_DIM));

	float* data = new float[DATA_NUM * DATA_DIM];
	inF.read(reinterpret_cast<char*>(data), DATA_DIM * DATA_NUM);
	
	inF.close();
	
	return data;
}

void fitdata(std::vector<Gaussian_Model> & models, float* fit_data, int iteration=1)
{
	float* data_prob = new float[COMPONENT_NUM * DATA_NUM];

	int i, j;
	float* prob = data_prob;
	int r;

	for (r = 0; r < iteration; r++)
	{
		//E-step
		float sum;
		for (i = 0; i < DATA_NUM; i++)
		{
			sum = 0.0f;
			for (j = 0; j < COMPONENT_NUM; j++)
			{
				prob[j] = models[j].getprior() * models[j].calprob(fit_data + i * DATA_DIM);
				sum += prob[j];
			}

			for (j = 0; j < COMPONENT_NUM; j++)
			{
				prob[j] /= (sum + 0.000001f);
			}

			prob += COMPONENT_NUM;
		}

		//M-step
		for (i = 0; i < COMPONENT_NUM; i++)
		{
			models[i].preprocess();
		}

		float maxprob;
		int comindex = 0;
		prob = data_prob;
		for (i = 0; i < DATA_NUM; i++)
		{
			maxprob = *prob;
			comindex = 0;
			for (j = 1; j < COMPONENT_NUM; j++)
			{
				if (prob[j] > maxprob)
				{
					maxprob = prob[j];
					comindex = j;
				}
			}

			models[comindex].updatestep(prob[comindex], fit_data + i * DATA_DIM);

			prob += COMPONENT_NUM;
		}

		for (i = 0; i < COMPONENT_NUM; i++)
		{
			models[i].postprocess(DATA_NUM);
		}
	}
	
	delete[] data_prob;
}

class Test
{
public:
	Test()
		: m_ptr()
	{
		m_ptr = new float[20];
	};

	~Test()
	{
		if (m_ptr)
			delete [] m_ptr;
	}

	void Init()
	{
		
	}

private:
	float* m_ptr;

};


int main(int /*argc*/, char* /*argv*/[])
{
	cout << sizeof(DATA_NUM) << " " << sizeof(DATA_DIM) << endl;

	//matrix<float, row_major, unbounded_array<float, std::allocator<float>>> c1;

	
	//identity_matrix<double, std::allocator> m(3, 3);

	//std::vector<Test> tests;
	////tests.resize(3);
	//Test test1;
	//Test test2;
	//Test test3;

	//shared_ptr<Test> ptest1(new Test());
	//shared_ptr<Test> ptest2(new Test());
	//shared_ptr<Test> ptest3(new Test());

	//tests.push_back(*ptest1);
	//tests.push_back(*ptest2);
	//tests.push_back(*ptest3);

	//int n;
	//for (n = 0;n < tests.size(); n++)
	//{
	//	tests[n].Init();
	//}

	//generatedata();

	float* fit_data = readdata();

	std::vector<Gaussian_Model> models;

	models.push_back(Gaussian_Model(DATA_DIM));
	models.push_back(Gaussian_Model(DATA_DIM));
	models.push_back(Gaussian_Model(DATA_DIM));

	models[0].init();
	models[0].setmean(0.0f);
	models[0].setdiagvar(1.0f);
	models[0].setprior(1.0f);

	models[1].init();
	models[1].setmean(1.0f);
	models[1].setdiagvar(1.0f);
	models[1].setprior(1.0f);

	models[2].init();
	models[2].setmean(-1.0f);
	models[2].setdiagvar(1.0f);
	models[2].setprior(1.0f);

	fitdata(models, fit_data);

	delete[] fit_data;

	int i;
	for (i = 0; i < COMPONENT_NUM; i++)
	{
		models[i].printinfo();
	}

	return 1;
}