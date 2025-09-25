def process_pdf_and_create_index(pdf_path):
    """PDF 파일을 처리하고 인덱스를 생성하는 함수"""
    # PDF 파일 로드 및 텍스트 추출
    pdf_reader = PdfReader(pdf_path)
    text_chunks = []

    # 모든 페이지의 텍스트 추출
    for page_num, page in enumerate(pdf_reader.pages):
        text = page.extract_text()
        if text.strip():  # 빈 페이지 제외
            # 페이지 번호 정보 포함
            text_with_metadata = f"[페이지 {page_num + 1}] {text}"
            text_chunks.append(text_with_metadata)

    # LlamaIndex Document 객체 생성
    documents = [Document(text=chunk) for chunk in text_chunks]

    # 문서 분할 (청킹)
    node_parser = SentenceSplitter(
        chunk_size=512,       # 청크 크기
        chunk_overlap=50,     # 오버랩
        paragraph_separator="\n\n",
        secondary_chunking_regex="(?<=\. )",
        include_metadata=True,
        include_prev_next_rel=True  # 이전/다음 청크 관계 포함
    )


    # Settings 설정
    Settings.llm = llm
    Settings.embed_model = embed_model
    Settings.node_parser = node_parser

    # 노드 파싱
    nodes = node_parser.get_nodes_from_documents(documents)

    # 인덱스 생성
    index = VectorStoreIndex(nodes)

    # 인덱스 저장
    index_dir = "pdf_index_storage"
    os.makedirs(index_dir, exist_ok=True)
    index.storage_context.persist(persist_dir=index_dir)

    return index


def load_saved_index():
    """저장된 인덱스 로드"""
    index_dir = "pdf_index_storage"
    if os.path.exists(index_dir):
        # 인덱스 로드
        storage_context = StorageContext.from_defaults(persist_dir=index_dir)
        index = load_index_from_storage(storage_context)
        return index
    return None

def create_optimized_query_engine(index):
    """최적화된 쿼리 엔진 생성"""
    # 검색기 설정 (Top-k 파라미터 조정)
    retriever = VectorIndexRetriever(
        index=index,
        similarity_top_k=5,  # 관련성 높은 문서 5개로 조정
        vector_store_query_mode="default"
    )

    # 유사도 임계값 설정
    node_postprocessors = [SimilarityPostprocessor(similarity_cutoff=0.2)]

    # 쿼리 엔진 생성
    query_engine = RetrieverQueryEngine.from_args(
        retriever=retriever,
        node_postprocessors=node_postprocessors,
        response_mode="compact",  # 모든 관련 문서를 한번에 고려
        response_kwargs={"verbose": True}  # 디버깅을 위한 verbose 모드
    )

    return query_engine
