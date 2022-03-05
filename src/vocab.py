class vocab: 
    # vocabulary class with flag words commonly attributed to misinformation
    # modified from https://www.mdpi.com/2078-2489/12/1/4/htm
    class subj: 
        article = ['article','submission' ,'sub' ,'post']
        title = ['title','headline','header']
        source = ['source' ,'website','site' ,'url','link'] 
        secpers = ['you']
        this = ['it','this','that','here'] 
        fpers = ['i','me','we'] 
    
    class pred:
        be = ['be']
        feel = ['look','sound' ,'feel' ,'seem' ,'smell' ,'stink'] 
        think = ['guess','think','beleive','say' ,'know','feel', 'suspect'] 
        believe = ['believe','fall','buy'] 
        call = ['call'] 
        stop = ['stop' ,'quit','refrain','do'] 
        report = ['flag' ,'report','remove']
        spread = ['spread' ,'propagate','spew','distribute', 'promote','post','submit'] 

    class obj:
        news = ['news','information','info']
        misinfo = ['disinformation','misinformation','malinformation'] 
        clickbait = ['clickbait','innacuracy','innacuracies'] 
        falsehood = ['falsehood','fabrication'] 
        bs = ['bullshit','bs'] 
        propaganda = ['propaganda'] 

    class attr:
        false = ['fake' ,'false' ,'bogus','fabricated', 'manipulated', 'manipulative', 'inaccurate']
        misleading = ['misleading','mislead','editorialized','editorialize', 'clickbait','sensationalized' ,'sensationalize', 'sensationalist']
        unreliable = ['untrustworthy','unreliable','unverified']
        bs = ['bullshit','bs'] 
        propaganda = ['propaganda'] 
        real = ['real','true','correct'] 
        reliable = ['reliable','verified','credible'] 
        
    class neg: 
        neg = ['not','no']