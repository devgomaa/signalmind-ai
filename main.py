from engine.pipelines.full_pipeline import FullPipeline




def main():


    pipeline = FullPipeline()


    result = pipeline.run()


    print("\n🔥 TOP TRENDS\n")


    for t in result["trends"][:5]:


        print(t)




if __name__ == "__main__":


    main()
