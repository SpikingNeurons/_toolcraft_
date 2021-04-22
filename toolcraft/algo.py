
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import pandas as pd
import numpy as np
import pyarrow as pa


def compute_pca_2_components(
    data_for_embedding: pa.Table, read_shuffled: bool = False
) -> pa.Table:
    
    # stack the pa.Table column to get 2D numpy array
    _data = np.vstack(np.asarray(data_for_embedding["data"]))

    # build shuffle indices especially needed when partitioned columns are
    # read where things are not stored in shuffled way
    if read_shuffled:
        np.random.seed(213123)
        _shuffled_indices = np.random.permutation(len(_data))
        np.random.seed(None)
        _data = _data[_shuffled_indices]
    
    # container for return data
    _container = {}
    
    # add fields used for scatter plots
    # get pca components
    if _data.shape[1] > 2:
        pca = PCA(n_components=2)
        pca_result = pca.fit_transform(_data)
    else:
        pca_result = _data
    
    # fill in pandas frame
    _container["PCA component 1"] = pca_result[:, 0]
    _container["PCA component 2"] = pca_result[:, 1]
    
    # add label and remaining fields if any which can be used for hovering
    # annotations
    for f in data_for_embedding.column_names:
        if f == "data":
            continue
        if read_shuffled:
            # noinspection PyUnboundLocalVariable
            _container[f] = np.asarray(data_for_embedding[f])[_shuffled_indices]
        else:
            _container[f] = np.asarray(data_for_embedding[f])
    
    # return
    return pa.table(
        _container,
    )


def compute_tsne_embeddings(
    data_for_embedding: pa.Table,
    pca_comp_for_embeddings: int = 40,
) -> pa.Table:
    
    # stack the pa.Table column to get 2D numpy array
    _data = np.vstack(np.asarray(data_for_embedding["data"]))
    
    # container for return data
    _container = {}
    
    # add fields used for scatter plots
    if _data.shape[1] == 2:
        _container["t-SNE component 1"] = _data[:, 0]
        _container["t-SNE component 2"] = _data[:, 1]
    else:
        # get pca components
        pca = PCA(
            n_components=min(
                pca_comp_for_embeddings, min(_data.shape)
            )
        )
        pca_result = pca.fit_transform(_data)
        
        # compute tsne
        tsne = TSNE(n_components=2)
        tsne_result = tsne.fit_transform(pca_result)
        
        # fill in pandas frame
        _container["t-SNE component 1"] = tsne_result[:, 0]
        _container["t-SNE component 2"] = tsne_result[:, 1]
    
    # add label and remaining fields if any which can be used for hovering
    # annotations
    for f in data_for_embedding.column_names:
        if f == "data":
            continue
        _container[f] = np.asarray(data_for_embedding[f])
    
    # return
    return pa.table(
        _container, metadata=data_for_embedding.schema.metadata
    )
